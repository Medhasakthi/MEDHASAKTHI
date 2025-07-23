"""
UPI Payment Service for MEDHASAKTHI
Handles UPI payment requests, QR generation, and verification
"""
import uuid
import qrcode
import io
import base64
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from decimal import Decimal
import urllib.parse

from app.models.upi_payment import (
    UPIConfiguration, UPIPaymentRequest, UPIPaymentVerification,
    UPIPaymentNotification, UPIPaymentStatus, UPIProvider
)
from app.services.email_service import email_service


class UPIPaymentService:
    """Service for UPI payment operations"""
    
    def __init__(self):
        self.payment_id_prefix = "UPI"
        self.qr_code_size = 300  # QR code size in pixels
        self.payment_timeout_minutes = 30  # Default payment timeout
    
    def create_payment_request(
        self,
        amount: float,
        description: str,
        user_data: Dict[str, Any],
        reference_id: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Create a new UPI payment request"""
        
        try:
            # Get active UPI configuration
            upi_config = db.query(UPIConfiguration).filter(
                UPIConfiguration.is_active == True,
                UPIConfiguration.is_primary == True
            ).first()
            
            if not upi_config:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="UPI payment service not configured"
                )
            
            # Validate amount
            if amount < float(upi_config.min_amount) or amount > float(upi_config.max_amount):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Amount must be between ₹{upi_config.min_amount} and ₹{upi_config.max_amount}"
                )
            
            # Generate payment ID
            payment_id = self._generate_payment_id()
            
            # Create payment note
            payment_note = f"MEDHASAKTHI-{payment_id}"
            if description:
                payment_note += f"-{description[:20]}"
            
            # Generate QR code and deep link
            qr_data, qr_image_base64, deep_link = self._generate_upi_qr(
                upi_config, amount, payment_note
            )
            
            # Calculate expiry time
            expires_at = datetime.utcnow() + timedelta(minutes=upi_config.verification_timeout_minutes)
            
            # Create payment request
            payment_request = UPIPaymentRequest(
                payment_id=payment_id,
                upi_config_id=upi_config.id,
                user_id=user_data.get('user_id'),
                user_email=user_data.get('email'),
                user_phone=user_data.get('phone'),
                user_name=user_data.get('name'),
                amount=Decimal(str(amount)),
                description=description,
                reference_id=reference_id,
                upi_id=upi_config.upi_id,
                upi_name=upi_config.upi_name,
                payment_note=payment_note,
                qr_code_data=qr_data,
                upi_deep_link=deep_link,
                expires_at=expires_at,
                metadata=user_data.get('metadata', {}),
                ip_address=user_data.get('ip_address'),
                user_agent=user_data.get('user_agent')
            )
            
            db.add(payment_request)
            db.commit()
            
            # Send notification to user
            if user_data.get('email'):
                self._send_payment_notification(
                    payment_request, "payment_created", db
                )
            
            return {
                "payment_id": payment_id,
                "amount": amount,
                "upi_id": upi_config.upi_id,
                "upi_name": upi_config.upi_name,
                "payment_note": payment_note,
                "qr_code_base64": qr_image_base64,
                "upi_deep_link": deep_link,
                "expires_at": expires_at.isoformat(),
                "instructions": self._get_payment_instructions(upi_config),
                "require_screenshot": upi_config.require_screenshot
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create payment request: {str(e)}"
            )
    
    def _generate_payment_id(self) -> str:
        """Generate unique payment ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_part = str(uuid.uuid4())[:8].upper()
        return f"{self.payment_id_prefix}{timestamp}{random_part}"
    
    def _generate_upi_qr(
        self,
        upi_config: UPIConfiguration,
        amount: float,
        payment_note: str
    ) -> Tuple[str, str, str]:
        """Generate UPI QR code and deep link"""
        
        # UPI URL format
        upi_url = f"upi://pay?pa={upi_config.upi_id}&pn={urllib.parse.quote(upi_config.upi_name)}"
        
        if upi_config.include_amount_in_qr:
            upi_url += f"&am={amount}"
        
        if upi_config.include_note_in_qr:
            upi_url += f"&tn={urllib.parse.quote(payment_note)}"
        
        upi_url += "&cu=INR"
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(upi_url)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        qr_image.save(buffer, format='PNG')
        qr_image_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return upi_url, qr_image_base64, upi_url
    
    def _get_payment_instructions(self, upi_config: UPIConfiguration) -> List[str]:
        """Get payment instructions for users"""
        
        instructions = [
            "1. Scan the QR code with any UPI app (PhonePe, Google Pay, Paytm, etc.)",
            "2. Verify the payment details (amount, UPI ID, name)",
            "3. Complete the payment using your UPI PIN",
            "4. Take a screenshot of the successful payment",
            "5. Upload the screenshot for verification"
        ]
        
        if not upi_config.require_screenshot:
            instructions = instructions[:-2]  # Remove screenshot steps
        
        return instructions
    
    def submit_payment_proof(
        self,
        payment_id: str,
        transaction_id: str,
        screenshot_data: Optional[str] = None,
        payment_method: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Submit payment proof by user"""
        
        try:
            # Find payment request
            payment_request = db.query(UPIPaymentRequest).filter(
                UPIPaymentRequest.payment_id == payment_id
            ).first()
            
            if not payment_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment request not found"
                )
            
            # Check if payment is still valid
            if payment_request.expires_at < datetime.utcnow():
                payment_request.status = UPIPaymentStatus.EXPIRED
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment request has expired"
                )
            
            # Update payment request
            payment_request.transaction_id = transaction_id
            payment_request.payment_method = payment_method
            payment_request.screenshot_url = screenshot_data  # In real app, save to storage
            payment_request.paid_at = datetime.utcnow()
            payment_request.verification_status = "pending"
            
            # Get UPI config for auto-verification
            upi_config = db.query(UPIConfiguration).filter(
                UPIConfiguration.id == payment_request.upi_config_id
            ).first()
            
            if upi_config and upi_config.auto_verify_payments:
                # Auto-verify payment
                payment_request.status = UPIPaymentStatus.SUCCESS
                payment_request.verification_status = "verified"
                payment_request.verified_at = datetime.utcnow()
                payment_request.verified_by = "system"
                
                # Update UPI config statistics
                upi_config.total_transactions += 1
                upi_config.total_amount += payment_request.amount
                
                # Send success notification
                self._send_payment_notification(
                    payment_request, "payment_success", db
                )
                
                message = "Payment verified automatically"
            else:
                # Manual verification required
                payment_request.status = UPIPaymentStatus.PENDING
                
                # Send verification notification to admin
                self._send_payment_notification(
                    payment_request, "verification_required", db
                )
                
                message = "Payment submitted for verification"
            
            db.commit()
            
            return {
                "status": "success",
                "message": message,
                "payment_status": payment_request.status.value,
                "verification_status": payment_request.verification_status,
                "auto_verified": upi_config.auto_verify_payments if upi_config else False
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to submit payment proof: {str(e)}"
            )
    
    def verify_payment(
        self,
        payment_id: str,
        verification_status: str,
        verified_by: str,
        notes: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Verify payment by admin"""
        
        try:
            # Find payment request
            payment_request = db.query(UPIPaymentRequest).filter(
                UPIPaymentRequest.payment_id == payment_id
            ).first()
            
            if not payment_request:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment request not found"
                )
            
            # Create verification record
            verification = UPIPaymentVerification(
                payment_request_id=payment_request.id,
                verified_by=verified_by,
                verification_status=verification_status,
                verification_notes=notes,
                verified_amount=payment_request.amount,
                verified_transaction_id=payment_request.transaction_id,
                verified_timestamp=datetime.utcnow()
            )
            
            db.add(verification)
            
            # Update payment request
            payment_request.verification_status = verification_status
            payment_request.verified_by = verified_by
            payment_request.verified_at = datetime.utcnow()
            payment_request.verification_notes = notes
            
            if verification_status == "verified":
                payment_request.status = UPIPaymentStatus.SUCCESS
                
                # Update UPI config statistics
                upi_config = db.query(UPIConfiguration).filter(
                    UPIConfiguration.id == payment_request.upi_config_id
                ).first()
                
                if upi_config:
                    upi_config.total_transactions += 1
                    upi_config.total_amount += payment_request.amount
                
                # Send success notification
                self._send_payment_notification(
                    payment_request, "payment_verified", db
                )
                
            elif verification_status == "rejected":
                payment_request.status = UPIPaymentStatus.FAILED
                
                # Send rejection notification
                self._send_payment_notification(
                    payment_request, "payment_rejected", db
                )
            
            db.commit()
            
            return {
                "status": "success",
                "message": f"Payment {verification_status} successfully",
                "payment_status": payment_request.status.value,
                "verification_status": verification_status
            }
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to verify payment: {str(e)}"
            )
    
    def get_payment_status(self, payment_id: str, db: Session) -> Dict[str, Any]:
        """Get payment status"""
        
        payment_request = db.query(UPIPaymentRequest).filter(
            UPIPaymentRequest.payment_id == payment_id
        ).first()
        
        if not payment_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment request not found"
            )
        
        return {
            "payment_id": payment_request.payment_id,
            "amount": float(payment_request.amount),
            "status": payment_request.status.value,
            "verification_status": payment_request.verification_status,
            "created_at": payment_request.created_at.isoformat(),
            "expires_at": payment_request.expires_at.isoformat() if payment_request.expires_at else None,
            "paid_at": payment_request.paid_at.isoformat() if payment_request.paid_at else None,
            "verified_at": payment_request.verified_at.isoformat() if payment_request.verified_at else None,
            "transaction_id": payment_request.transaction_id,
            "description": payment_request.description,
            "reference_id": payment_request.reference_id
        }
    
    def _send_payment_notification(
        self,
        payment_request: UPIPaymentRequest,
        notification_type: str,
        db: Session
    ):
        """Send payment notification"""
        
        try:
            # Create notification record
            notification = UPIPaymentNotification(
                payment_request_id=payment_request.id,
                notification_type=notification_type,
                recipient_type="user",
                recipient_email=payment_request.user_email,
                template_used=f"upi_{notification_type}"
            )
            
            # Generate email content based on notification type
            if notification_type == "payment_created":
                subject = f"Payment Request Created - ₹{payment_request.amount}"
                message = f"""
                Dear {payment_request.user_name},
                
                Your payment request has been created successfully.
                
                Payment Details:
                - Payment ID: {payment_request.payment_id}
                - Amount: ₹{payment_request.amount}
                - Description: {payment_request.description}
                
                Please complete the payment using the provided UPI details.
                
                Best regards,
                MEDHASAKTHI Team
                """
            
            elif notification_type == "payment_success":
                subject = f"Payment Successful - ₹{payment_request.amount}"
                message = f"""
                Dear {payment_request.user_name},
                
                Your payment has been successfully verified!
                
                Payment Details:
                - Payment ID: {payment_request.payment_id}
                - Amount: ₹{payment_request.amount}
                - Transaction ID: {payment_request.transaction_id}
                
                Thank you for your payment.
                
                Best regards,
                MEDHASAKTHI Team
                """
            
            elif notification_type == "payment_rejected":
                subject = f"Payment Verification Failed - ₹{payment_request.amount}"
                message = f"""
                Dear {payment_request.user_name},
                
                Unfortunately, your payment could not be verified.
                
                Payment Details:
                - Payment ID: {payment_request.payment_id}
                - Amount: ₹{payment_request.amount}
                - Reason: {payment_request.verification_notes or 'Payment verification failed'}
                
                Please contact support for assistance.
                
                Best regards,
                MEDHASAKTHI Team
                """
            
            else:
                return  # Unknown notification type
            
            notification.subject = subject
            notification.message = message
            
            db.add(notification)
            
            # Send email
            if payment_request.user_email:
                email_service.send_email(
                    to_email=payment_request.user_email,
                    subject=subject,
                    content=message
                )
                notification.delivery_status = "sent"
                notification.delivered_at = datetime.utcnow()
            
            db.commit()
            
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")
    
    def get_pending_verifications(self, db: Session) -> List[Dict[str, Any]]:
        """Get payments pending verification"""
        
        pending_payments = db.query(UPIPaymentRequest).filter(
            UPIPaymentRequest.verification_status == "pending",
            UPIPaymentRequest.status == UPIPaymentStatus.PENDING
        ).order_by(UPIPaymentRequest.created_at.desc()).all()
        
        return [
            {
                "payment_id": payment.payment_id,
                "amount": float(payment.amount),
                "user_name": payment.user_name,
                "user_email": payment.user_email,
                "description": payment.description,
                "transaction_id": payment.transaction_id,
                "payment_method": payment.payment_method,
                "screenshot_url": payment.screenshot_url,
                "created_at": payment.created_at.isoformat(),
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
            }
            for payment in pending_payments
        ]


# Global instance
upi_payment_service = UPIPaymentService()
