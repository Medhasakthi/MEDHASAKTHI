"""
Certificate models for MEDHASAKTHI
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer, 
    Float, JSON, ForeignKey, func, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class CertificateType(str, Enum):
    """Certificate types"""
    COURSE_COMPLETION = "course_completion"
    EXAM_PASS = "exam_pass"
    ACHIEVEMENT = "achievement"
    PARTICIPATION = "participation"
    PROFESSIONAL = "professional"
    SKILL_VERIFICATION = "skill_verification"


class CertificateStatus(str, Enum):
    """Certificate status"""
    DRAFT = "draft"
    GENERATED = "generated"
    ISSUED = "issued"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ProfessionCategory(str, Enum):
    """Professional categories for certificate templates"""
    INFORMATION_TECHNOLOGY = "information_technology"
    HEALTHCARE = "healthcare"
    FINANCE_ACCOUNTING = "finance_accounting"
    ENGINEERING = "engineering"
    MANAGEMENT = "management"
    EDUCATION = "education"
    LEGAL = "legal"
    MARKETING = "marketing"
    DESIGN_CREATIVE = "design_creative"
    DATA_SCIENCE = "data_science"
    CYBERSECURITY = "cybersecurity"
    PROJECT_MANAGEMENT = "project_management"
    DIGITAL_MARKETING = "digital_marketing"
    CLOUD_COMPUTING = "cloud_computing"
    GENERAL = "general"


class CertificateTemplate(Base):
    """Certificate templates for different professions and types"""
    __tablename__ = "certificate_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Template identification
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Template categorization
    certificate_type = Column(String(50), nullable=False, index=True)
    profession_category = Column(String(50), nullable=False, index=True)
    
    # Template design
    template_data = Column(JSON, nullable=False)  # Layout, fonts, colors, positioning
    background_image_url = Column(String(500))
    border_style = Column(JSON)  # Border design specifications
    
    # Logo and watermark settings
    logo_position = Column(JSON)  # Position and size for MEDHASAKTHI logo
    watermark_settings = Column(JSON)  # Watermark opacity, position, size
    
    # Template metadata
    dimensions = Column(JSON)  # Width, height, DPI
    orientation = Column(String(20), default="landscape")  # landscape, portrait
    
    # Status and versioning
    version = Column(String(20), default="1.0")
    is_active = Column(Boolean, default=True, index=True)
    is_default = Column(Boolean, default=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    certificates = relationship("Certificate", back_populates="template")
    
    def __repr__(self):
        return f"<CertificateTemplate(name={self.name}, category={self.profession_category})>"


class Certificate(Base):
    """Generated certificates"""
    __tablename__ = "certificates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Certificate identification
    certificate_number = Column(String(50), unique=True, nullable=False, index=True)
    verification_code = Column(String(100), unique=True, nullable=False, index=True)
    
    # Certificate details
    title = Column(String(300), nullable=False)
    description = Column(Text)
    certificate_type = Column(String(50), nullable=False, index=True)
    
    # Recipient information
    recipient_name = Column(String(200), nullable=False)
    recipient_email = Column(String(255), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"))
    
    # Institution information
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    issued_by = Column(String(200))  # Name of issuing authority
    
    # Academic/Professional details
    subject_name = Column(String(200))
    course_name = Column(String(200))
    exam_name = Column(String(200))
    score = Column(Float)
    grade = Column(String(20))
    completion_date = Column(DateTime(timezone=True))
    
    # Template and generation
    template_id = Column(UUID(as_uuid=True), ForeignKey("certificate_templates.id"), nullable=False)
    generation_data = Column(JSON)  # Data used for generation
    
    # File information
    pdf_url = Column(String(500))
    pdf_file_size = Column(Integer)
    thumbnail_url = Column(String(500))
    
    # Verification and security
    blockchain_hash = Column(String(128))  # For blockchain verification
    digital_signature = Column(Text)
    qr_code_data = Column(Text)
    
    # Status and validity
    status = Column(String(20), default=CertificateStatus.DRAFT, index=True)
    is_public = Column(Boolean, default=False)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    
    # Timestamps
    issued_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    template = relationship("CertificateTemplate", back_populates="certificates")
    student = relationship("Student")
    institute = relationship("Institute")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_certificate_recipient', 'recipient_email', 'institute_id'),
        Index('idx_certificate_status_date', 'status', 'issued_at'),
        Index('idx_certificate_verification', 'verification_code', 'status'),
    )
    
    def __repr__(self):
        return f"<Certificate(number={self.certificate_number}, recipient={self.recipient_name})>"


class CertificateGeneration(Base):
    """Certificate generation history and batch operations"""
    __tablename__ = "certificate_generations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Generation details
    batch_id = Column(String(100), index=True)  # For bulk generations
    generation_type = Column(String(50), nullable=False)  # single, bulk, automated
    
    # Request information
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    
    # Generation parameters
    template_id = Column(UUID(as_uuid=True), ForeignKey("certificate_templates.id"))
    generation_params = Column(JSON)  # Parameters used for generation
    
    # Results
    certificates_requested = Column(Integer, default=0)
    certificates_generated = Column(Integer, default=0)
    certificates_failed = Column(Integer, default=0)
    
    # Processing information
    processing_time = Column(Float)  # Time taken in seconds
    error_details = Column(JSON)  # Error information if any
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    requested_by_user = relationship("User")
    institute = relationship("Institute")
    template = relationship("CertificateTemplate")
    
    def __repr__(self):
        return f"<CertificateGeneration(batch_id={self.batch_id}, status={self.status})>"
