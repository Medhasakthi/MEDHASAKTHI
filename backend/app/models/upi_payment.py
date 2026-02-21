"""
UPI Payment Models for MEDHASAKTHI
Super admin configurable UPI payment system
"""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Enum as SQLEnum, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class UPIProvider(str, Enum):
    """UPI payment providers"""
    PHONEPE = "phonepe"
    GOOGLEPAY = "googlepay"
    PAYTM = "paytm"
    BHIM = "bhim"
    AMAZON_PAY = "amazon_pay"
    WHATSAPP_PAY = "whatsapp_pay"
    OTHER = "other"


class UPIPaymentStatus(str, Enum):
    """UPI payment status"""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class UPIConfiguration(Base):
    """Super admin UPI configuration"""
    __tablename__ = "upi_configuration"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # UPI Details
    upi_id = Column(String(100), nullable=False)  # e.g., medhasakthi@paytm
    upi_name = Column(String(200), nullable=False)  # Account holder name
    provider = Column(SQLEnum(UPIProvider), nullable=False)
    
    # Configuration
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)  # Primary UPI for payments
    
    # Display Information
    display_name = Column(String(100))  # e.g., "MEDHASAKTHI Education"
    description = Column(Text)  # Additional info for users
    
    # QR Code Configuration
    qr_code_url = Column(String(500))  # URL to QR code image
    qr_code_data = Column(Text)  # QR code data string
    
    # Payment Limits
    min_amount = Column(Numeric(10, 2), default=1.00)
    max_amount = Column(Numeric(10, 2), default=100000.00)
    daily_limit = Column(Numeric(15, 2))  # Daily transaction limit
    
    # Auto-generation Settings
    auto_generate_qr = Column(Boolean, default=True)
    include_amount_in_qr = Column(Boolean, default=True)
    include_note_in_qr = Column(Boolean, default=True)
    
    # Verification Settings
    require_screenshot = Column(Boolean, default=True)
    auto_verify_payments = Column(Boolean, default=False)
    verification_timeout_minutes = Column(Integer, default=30)
    
    # Notification Settings
    notify_on_payment = Column(Boolean, default=True)
    notification_email = Column(String(255))
    notification_phone = Column(String(20))
    
    # Usage Statistics
    total_transactions = Column(Integer, default=0)
    total_amount = Column(Numeric(15, 2), default=0)
    success_rate = Column(Numeric(5, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100))  # Super admin who created
    
    def __repr__(self):
        return f"<UPIConfiguration {self.upi_id}>"


class UPIPaymentRequest(Base):
    """UPI payment requests generated for users"""
    __tablename__ = "upi_payment_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Request Information
    payment_id = Column(String(100), unique=True, nullable=False, index=True)
    upi_config_id = Column(UUID(as_uuid=True), nullable=False)
    
    # User Information
    user_id = Column(UUID(as_uuid=True))  # Can be null for guest payments
    user_email = Column(String(255))
    user_phone = Column(String(20))
    user_name = Column(String(200))
    
    # Payment Details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR")
    description = Column(String(500))
    reference_id = Column(String(100))  # Internal reference (exam registration, etc.)
    
    # UPI Payment Information
    upi_id = Column(String(100), nullable=False)
    upi_name = Column(String(200), nullable=False)
    payment_note = Column(String(200))  # Note for UPI transaction
    
    # QR Code Information
    qr_code_url = Column(String(500))
    qr_code_data = Column(Text)
    upi_deep_link = Column(Text)  # Deep link for UPI apps
    
    # Payment Status
    status = Column(SQLEnum(UPIPaymentStatus), default=UPIPaymentStatus.PENDING)
    payment_method = Column(String(50))  # Which UPI app was used
    transaction_id = Column(String(100))  # UPI transaction ID from user
    
    # Verification
    screenshot_url = Column(String(500))  # Payment screenshot uploaded by user
    verification_status = Column(String(20), default="pending")  # pending, verified, rejected
    verified_by = Column(String(100))  # Admin who verified
    verification_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))  # Payment expiry time
    paid_at = Column(DateTime(timezone=True))
    verified_at = Column(DateTime(timezone=True))
    
    # Retry Information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Metadata
    metadata = Column(JSON)  # Additional data (exam details, etc.)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    def __repr__(self):
        return f"<UPIPaymentRequest {self.payment_id}: ₹{self.amount}>"


class UPIPaymentVerification(Base):
    """Manual payment verification by admins"""
    __tablename__ = "upi_payment_verifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_request_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Verification Details
    verified_by = Column(String(100), nullable=False)
    verification_status = Column(String(20), nullable=False)  # verified, rejected
    verification_notes = Column(Text)
    
    # Payment Verification Data
    verified_amount = Column(Numeric(10, 2))
    verified_transaction_id = Column(String(100))
    verified_timestamp = Column(DateTime(timezone=True))
    
    # Admin Information
    admin_ip = Column(String(50))
    admin_user_agent = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UPIPaymentVerification {self.verification_status}>"


class UPIPaymentNotification(Base):
    """Notifications sent for UPI payments"""
    __tablename__ = "upi_payment_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_request_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Notification Details
    notification_type = Column(String(50), nullable=False)  # payment_created, payment_success, etc.
    recipient_type = Column(String(20), nullable=False)  # user, admin
    recipient_email = Column(String(255))
    recipient_phone = Column(String(20))
    
    # Message Content
    subject = Column(String(200))
    message = Column(Text)
    template_used = Column(String(100))
    
    # Delivery Status
    delivery_status = Column(String(20), default="pending")  # pending, sent, failed
    delivery_attempts = Column(Integer, default=0)
    delivered_at = Column(DateTime(timezone=True))
    failure_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UPIPaymentNotification {self.notification_type}>"


class UPIPaymentAnalytics(Base):
    """Analytics data for UPI payments"""
    __tablename__ = "upi_payment_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Time Period
    date = Column(DateTime(timezone=True), nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # UPI Configuration
    upi_config_id = Column(UUID(as_uuid=True))
    
    # Payment Metrics
    total_requests = Column(Integer, default=0)
    successful_payments = Column(Integer, default=0)
    failed_payments = Column(Integer, default=0)
    pending_payments = Column(Integer, default=0)
    
    # Amount Metrics
    total_amount_requested = Column(Numeric(15, 2), default=0)
    total_amount_received = Column(Numeric(15, 2), default=0)
    average_transaction_amount = Column(Numeric(10, 2), default=0)
    
    # Performance Metrics
    success_rate = Column(Numeric(5, 2), default=0)
    average_verification_time = Column(Integer, default=0)  # in minutes
    
    # User Behavior
    unique_users = Column(Integer, default=0)
    repeat_users = Column(Integer, default=0)
    
    # Provider Analytics
    provider_breakdown = Column(JSON)  # Usage by UPI provider
    amount_range_breakdown = Column(JSON)  # Payments by amount ranges
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UPIPaymentAnalytics {self.date} - {self.period_type}>"
