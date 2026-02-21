"""
Unit tests for UPI Payment Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.upi_payment_service import upi_payment_service
from app.models.upi_payment import (
    UPIConfiguration, UPIPaymentRequest, UPIPaymentStatus, UPIProvider
)


class TestUPIPaymentService:
    """Test cases for UPI Payment Service"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_upi_config(self):
        """Sample UPI configuration"""
        config = Mock(spec=UPIConfiguration)
        config.id = "config-123"
        config.upi_id = "medhasakthi@paytm"
        config.upi_name = "MEDHASAKTHI Education"
        config.provider = UPIProvider.PAYTM
        config.is_active = True
        config.is_primary = True
        config.min_amount = Decimal("1.00")
        config.max_amount = Decimal("100000.00")
        config.include_amount_in_qr = True
        config.include_note_in_qr = True
        config.require_screenshot = True
        config.auto_verify_payments = False
        config.verification_timeout_minutes = 30
        return config
    
    @pytest.fixture
    def sample_user_data(self):
        """Sample user data for payment"""
        return {
            "user_id": "user-123",
            "email": "john.doe@example.com",
            "phone": "+91-9876543210",
            "name": "John Doe",
            "metadata": {"exam_id": "exam-123"},
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0..."
        }
    
    @pytest.fixture
    def sample_payment_request(self):
        """Sample payment request"""
        payment = Mock(spec=UPIPaymentRequest)
        payment.id = "payment-123"
        payment.payment_id = "UPI20240120123456ABCD1234"
        payment.amount = Decimal("500.00")
        payment.upi_id = "medhasakthi@paytm"
        payment.upi_name = "MEDHASAKTHI Education"
        payment.status = UPIPaymentStatus.PENDING
        payment.verification_status = "pending"
        payment.expires_at = datetime.utcnow() + timedelta(minutes=30)
        payment.user_email = "john.doe@example.com"
        payment.user_name = "John Doe"
        payment.description = "Exam Registration Fee"
        return payment
    
    def test_generate_payment_id(self):
        """Test payment ID generation"""
        payment_id = upi_payment_service._generate_payment_id()
        
        assert payment_id.startswith("UPI")
        assert len(payment_id) >= 20  # UPI + timestamp + random part
        
        # Test uniqueness
        payment_id2 = upi_payment_service._generate_payment_id()
        assert payment_id != payment_id2
    
    @patch('app.services.upi_payment_service.qrcode.QRCode')
    def test_generate_upi_qr(self, mock_qrcode, sample_upi_config):
        """Test UPI QR code generation"""
        # Setup mock QR code
        mock_qr_instance = Mock()
        mock_qr_image = Mock()
        mock_qr_image.save = Mock()
        mock_qr_instance.make_image.return_value = mock_qr_image
        mock_qrcode.return_value = mock_qr_instance
        
        # Test QR generation
        upi_url, qr_base64, deep_link = upi_payment_service._generate_upi_qr(
            sample_upi_config, 500.00, "TEST-PAYMENT"
        )
        
        # Assertions
        assert upi_url.startswith("upi://pay")
        assert "medhasakthi@paytm" in upi_url
        assert "am=500.0" in upi_url
        assert "tn=TEST-PAYMENT" in upi_url
        assert qr_base64 is not None
        assert deep_link == upi_url
    
    @patch('app.services.upi_payment_service.upi_payment_service._generate_upi_qr')
    @patch('app.services.upi_payment_service.upi_payment_service._send_payment_notification')
    def test_create_payment_request_success(
        self, 
        mock_send_notification, 
        mock_generate_qr, 
        mock_db, 
        sample_upi_config, 
        sample_user_data
    ):
        """Test successful payment request creation"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_upi_config
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_generate_qr.return_value = ("upi://pay?...", "base64data", "upi://pay?...")
        mock_send_notification.return_value = None
        
        # Test
        result = upi_payment_service.create_payment_request(
            amount=500.00,
            description="Test Payment",
            user_data=sample_user_data,
            reference_id="ref-123",
            db=mock_db
        )
        
        # Assertions
        assert "payment_id" in result
        assert result["amount"] == 500.00
        assert result["upi_id"] == "medhasakthi@paytm"
        assert "qr_code_base64" in result
        assert "expires_at" in result
        assert mock_db.add.called
        assert mock_db.commit.called
    
    def test_create_payment_request_no_config(self, mock_db, sample_user_data):
        """Test payment request creation when no UPI config exists"""
        # Setup mock to return no config
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test should raise HTTPException
        with pytest.raises(Exception) as exc_info:
            upi_payment_service.create_payment_request(
                amount=500.00,
                description="Test Payment",
                user_data=sample_user_data,
                db=mock_db
            )
        
        assert "not configured" in str(exc_info.value).lower()
    
    def test_create_payment_request_invalid_amount(self, mock_db, sample_upi_config, sample_user_data):
        """Test payment request creation with invalid amount"""
        # Setup mock
        mock_db.query.return_value.filter.return_value.first.return_value = sample_upi_config
        
        # Test with amount below minimum
        with pytest.raises(Exception) as exc_info:
            upi_payment_service.create_payment_request(
                amount=0.50,  # Below minimum of 1.00
                description="Test Payment",
                user_data=sample_user_data,
                db=mock_db
            )
        
        assert "amount must be between" in str(exc_info.value).lower()
    
    @patch('app.services.upi_payment_service.upi_payment_service._send_payment_notification')
    def test_submit_payment_proof_success(
        self, 
        mock_send_notification, 
        mock_db, 
        sample_payment_request, 
        sample_upi_config
    ):
        """Test successful payment proof submission"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_payment_request,  # Payment request query
            sample_upi_config        # UPI config query
        ]
        mock_db.commit = Mock()
        mock_send_notification.return_value = None
        
        # Test
        result = upi_payment_service.submit_payment_proof(
            payment_id="UPI20240120123456ABCD1234",
            transaction_id="TXN123456789",
            screenshot_data="screenshot_url",
            payment_method="phonepe",
            db=mock_db
        )
        
        # Assertions
        assert result["status"] == "success"
        assert "payment_status" in result
        assert mock_db.commit.called
    
    def test_submit_payment_proof_expired(self, mock_db, sample_payment_request):
        """Test payment proof submission for expired payment"""
        # Setup expired payment
        sample_payment_request.expires_at = datetime.utcnow() - timedelta(minutes=10)
        mock_db.query.return_value.filter.return_value.first.return_value = sample_payment_request
        mock_db.commit = Mock()
        
        # Test should raise exception
        with pytest.raises(Exception) as exc_info:
            upi_payment_service.submit_payment_proof(
                payment_id="UPI20240120123456ABCD1234",
                transaction_id="TXN123456789",
                db=mock_db
            )
        
        assert "expired" in str(exc_info.value).lower()
    
    def test_submit_payment_proof_not_found(self, mock_db):
        """Test payment proof submission for non-existent payment"""
        # Setup mock to return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test should raise exception
        with pytest.raises(Exception) as exc_info:
            upi_payment_service.submit_payment_proof(
                payment_id="INVALID_ID",
                transaction_id="TXN123456789",
                db=mock_db
            )
        
        assert "not found" in str(exc_info.value).lower()
    
    @patch('app.services.upi_payment_service.upi_payment_service._send_payment_notification')
    def test_verify_payment_success(
        self, 
        mock_send_notification, 
        mock_db, 
        sample_payment_request, 
        sample_upi_config
    ):
        """Test successful payment verification"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            sample_payment_request,  # Payment request query
            sample_upi_config        # UPI config query
        ]
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_send_notification.return_value = None
        
        # Test
        result = upi_payment_service.verify_payment(
            payment_id="UPI20240120123456ABCD1234",
            verification_status="verified",
            verified_by="admin@medhasakthi.com",
            notes="Payment verified successfully",
            db=mock_db
        )
        
        # Assertions
        assert result["status"] == "success"
        assert result["verification_status"] == "verified"
        assert mock_db.add.called  # Verification record added
        assert mock_db.commit.called
    
    def test_verify_payment_rejection(
        self, 
        mock_db, 
        sample_payment_request
    ):
        """Test payment verification rejection"""
        # Setup mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_payment_request
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        # Test
        result = upi_payment_service.verify_payment(
            payment_id="UPI20240120123456ABCD1234",
            verification_status="rejected",
            verified_by="admin@medhasakthi.com",
            notes="Invalid transaction ID",
            db=mock_db
        )
        
        # Assertions
        assert result["status"] == "success"
        assert result["verification_status"] == "rejected"
        # Payment status should be updated to failed
        assert sample_payment_request.status == UPIPaymentStatus.FAILED
    
    def test_get_payment_status(self, mock_db, sample_payment_request):
        """Test getting payment status"""
        # Setup mock
        mock_db.query.return_value.filter.return_value.first.return_value = sample_payment_request
        
        # Test
        status_data = upi_payment_service.get_payment_status(
            "UPI20240120123456ABCD1234", mock_db
        )
        
        # Assertions
        assert status_data["payment_id"] == "UPI20240120123456ABCD1234"
        assert status_data["amount"] == 500.00
        assert status_data["status"] == "pending"
        assert "created_at" in status_data
        assert "expires_at" in status_data
    
    def test_get_payment_status_not_found(self, mock_db):
        """Test getting status for non-existent payment"""
        # Setup mock to return None
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Test should raise exception
        with pytest.raises(Exception) as exc_info:
            upi_payment_service.get_payment_status("INVALID_ID", mock_db)
        
        assert "not found" in str(exc_info.value).lower()
    
    def test_get_pending_verifications(self, mock_db):
        """Test getting pending payment verifications"""
        # Setup mock payments
        pending_payment1 = Mock()
        pending_payment1.payment_id = "PAY1"
        pending_payment1.amount = Decimal("500.00")
        pending_payment1.user_name = "John Doe"
        pending_payment1.user_email = "john@example.com"
        pending_payment1.description = "Test Payment 1"
        pending_payment1.transaction_id = "TXN123"
        pending_payment1.payment_method = "phonepe"
        pending_payment1.screenshot_url = "screenshot1.jpg"
        pending_payment1.created_at = datetime.utcnow()
        pending_payment1.paid_at = datetime.utcnow()
        
        mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            pending_payment1
        ]
        
        # Test
        pending_payments = upi_payment_service.get_pending_verifications(mock_db)
        
        # Assertions
        assert len(pending_payments) == 1
        assert pending_payments[0]["payment_id"] == "PAY1"
        assert pending_payments[0]["amount"] == 500.00
        assert pending_payments[0]["user_name"] == "John Doe"
    
    @patch('app.services.upi_payment_service.email_service.send_email')
    def test_send_payment_notification(self, mock_send_email, mock_db, sample_payment_request):
        """Test sending payment notification"""
        # Setup mock
        mock_send_email.return_value = True
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        # Test
        upi_payment_service._send_payment_notification(
            sample_payment_request, "payment_created", mock_db
        )
        
        # Assertions
        assert mock_send_email.called
        assert mock_db.add.called  # Notification record added
        assert mock_db.commit.called
    
    def test_get_payment_instructions(self, sample_upi_config):
        """Test getting payment instructions"""
        instructions = upi_payment_service._get_payment_instructions(sample_upi_config)
        
        assert isinstance(instructions, list)
        assert len(instructions) > 0
        assert any("scan" in instruction.lower() for instruction in instructions)
        assert any("screenshot" in instruction.lower() for instruction in instructions)
    
    def test_get_payment_instructions_no_screenshot(self, sample_upi_config):
        """Test getting payment instructions when screenshot not required"""
        sample_upi_config.require_screenshot = False
        
        instructions = upi_payment_service._get_payment_instructions(sample_upi_config)
        
        assert isinstance(instructions, list)
        assert not any("screenshot" in instruction.lower() for instruction in instructions)
    
    @patch('app.services.upi_payment_service.datetime')
    def test_payment_expiry_calculation(self, mock_datetime, mock_db, sample_upi_config, sample_user_data):
        """Test payment expiry time calculation"""
        # Setup mock datetime
        fixed_time = datetime(2024, 1, 20, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time
        
        # Setup other mocks
        mock_db.query.return_value.filter.return_value.first.return_value = sample_upi_config
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        with patch.object(upi_payment_service, '_generate_upi_qr') as mock_qr:
            mock_qr.return_value = ("upi://pay", "base64", "upi://pay")
            
            # Test
            result = upi_payment_service.create_payment_request(
                amount=500.00,
                description="Test Payment",
                user_data=sample_user_data,
                db=mock_db
            )
            
            # Verify expiry time is 30 minutes from now
            expected_expiry = fixed_time + timedelta(minutes=30)
            assert result["expires_at"] == expected_expiry.isoformat()


if __name__ == "__main__":
    pytest.main([__file__])
