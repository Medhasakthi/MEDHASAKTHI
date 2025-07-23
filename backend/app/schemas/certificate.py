"""
Certificate schemas for MEDHASAKTHI API
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class CertificateTypeEnum(str, Enum):
    """Certificate types"""
    COURSE_COMPLETION = "course_completion"
    EXAM_PASS = "exam_pass"
    ACHIEVEMENT = "achievement"
    PARTICIPATION = "participation"
    PROFESSIONAL = "professional"
    SKILL_VERIFICATION = "skill_verification"


class CertificateStatusEnum(str, Enum):
    """Certificate status"""
    DRAFT = "draft"
    GENERATED = "generated"
    ISSUED = "issued"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ProfessionCategoryEnum(str, Enum):
    """Professional categories"""
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


# Template Schemas
class CertificateTemplateCreateSchema(BaseModel):
    """Schema for creating certificate templates"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    certificate_type: CertificateTypeEnum
    profession_category: ProfessionCategoryEnum
    template_data: Dict[str, Any]
    background_image_url: Optional[str] = None
    border_style: Optional[Dict[str, Any]] = None
    logo_position: Optional[Dict[str, Any]] = None
    watermark_settings: Optional[Dict[str, Any]] = None
    dimensions: Optional[Dict[str, Any]] = None
    orientation: str = Field(default="landscape", regex="^(landscape|portrait)$")
    version: str = Field(default="1.0", max_length=20)
    is_default: bool = False


class CertificateTemplateUpdateSchema(BaseModel):
    """Schema for updating certificate templates"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    template_data: Optional[Dict[str, Any]] = None
    background_image_url: Optional[str] = None
    border_style: Optional[Dict[str, Any]] = None
    logo_position: Optional[Dict[str, Any]] = None
    watermark_settings: Optional[Dict[str, Any]] = None
    dimensions: Optional[Dict[str, Any]] = None
    orientation: Optional[str] = Field(None, regex="^(landscape|portrait)$")
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class CertificateTemplateResponseSchema(BaseModel):
    """Schema for certificate template response"""
    id: str
    name: str
    code: str
    description: Optional[str]
    certificate_type: str
    profession_category: str
    template_data: Dict[str, Any]
    background_image_url: Optional[str]
    border_style: Optional[Dict[str, Any]]
    logo_position: Optional[Dict[str, Any]]
    watermark_settings: Optional[Dict[str, Any]]
    dimensions: Optional[Dict[str, Any]]
    orientation: str
    version: str
    is_active: bool
    is_default: bool
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# Certificate Schemas
class CertificateCreateSchema(BaseModel):
    """Schema for creating certificates"""
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    certificate_type: CertificateTypeEnum
    recipient_name: str = Field(..., min_length=1, max_length=200)
    recipient_email: EmailStr
    student_id: Optional[str] = None
    issued_by: Optional[str] = Field(None, max_length=200)
    subject_name: Optional[str] = Field(None, max_length=200)
    course_name: Optional[str] = Field(None, max_length=200)
    exam_name: Optional[str] = Field(None, max_length=200)
    score: Optional[float] = Field(None, ge=0, le=100)
    grade: Optional[str] = Field(None, max_length=20)
    completion_date: Optional[datetime] = None
    template_id: str
    generation_data: Optional[Dict[str, Any]] = None
    is_public: bool = False
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class CertificateBulkCreateSchema(BaseModel):
    """Schema for bulk certificate creation"""
    template_id: str
    certificate_type: CertificateTypeEnum
    certificates: List[Dict[str, Any]] = Field(..., min_items=1, max_items=1000)
    issued_by: Optional[str] = None
    generation_params: Optional[Dict[str, Any]] = None


class CertificateUpdateSchema(BaseModel):
    """Schema for updating certificates"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    issued_by: Optional[str] = Field(None, max_length=200)
    score: Optional[float] = Field(None, ge=0, le=100)
    grade: Optional[str] = Field(None, max_length=20)
    is_public: Optional[bool] = None
    status: Optional[CertificateStatusEnum] = None
    valid_until: Optional[datetime] = None


class CertificateResponseSchema(BaseModel):
    """Schema for certificate response"""
    id: str
    certificate_number: str
    verification_code: str
    title: str
    description: Optional[str]
    certificate_type: str
    recipient_name: str
    recipient_email: str
    student_id: Optional[str]
    institute_id: str
    issued_by: Optional[str]
    subject_name: Optional[str]
    course_name: Optional[str]
    exam_name: Optional[str]
    score: Optional[float]
    grade: Optional[str]
    completion_date: Optional[datetime]
    template_id: str
    pdf_url: Optional[str]
    pdf_file_size: Optional[int]
    thumbnail_url: Optional[str]
    blockchain_hash: Optional[str]
    qr_code_data: Optional[str]
    status: str
    is_public: bool
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    issued_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CertificateVerificationSchema(BaseModel):
    """Schema for certificate verification"""
    verification_code: str = Field(..., min_length=1)


class CertificateVerificationResponseSchema(BaseModel):
    """Schema for certificate verification response"""
    is_valid: bool
    certificate: Optional[CertificateResponseSchema] = None
    verification_details: Dict[str, Any]
    verified_at: datetime


# Generation Schemas
class CertificateGenerationRequestSchema(BaseModel):
    """Schema for certificate generation request"""
    template_id: Optional[str] = None
    profession_category: Optional[ProfessionCategoryEnum] = None
    certificate_type: CertificateTypeEnum
    generation_type: str = Field(default="single", regex="^(single|bulk|automated)$")
    certificates: List[CertificateCreateSchema] = Field(..., min_items=1, max_items=1000)
    generation_params: Optional[Dict[str, Any]] = None


class CertificateGenerationResponseSchema(BaseModel):
    """Schema for certificate generation response"""
    success: bool
    message: str
    batch_id: Optional[str] = None
    generation_id: str
    certificates_requested: int
    certificates_generated: int
    certificates_failed: int
    processing_time: float
    generated_certificates: List[CertificateResponseSchema]
    errors: Optional[List[Dict[str, Any]]] = None


class CertificateSearchSchema(BaseModel):
    """Schema for certificate search"""
    query: Optional[str] = None
    certificate_type: Optional[CertificateTypeEnum] = None
    profession_category: Optional[ProfessionCategoryEnum] = None
    status: Optional[CertificateStatusEnum] = None
    recipient_email: Optional[EmailStr] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class CertificateSearchResponseSchema(BaseModel):
    """Schema for certificate search response"""
    certificates: List[CertificateResponseSchema]
    total: int
    page: int
    limit: int
    total_pages: int


class CertificateStatsSchema(BaseModel):
    """Schema for certificate statistics"""
    total_certificates: int
    certificates_by_type: Dict[str, int]
    certificates_by_status: Dict[str, int]
    certificates_by_profession: Dict[str, int]
    recent_certificates: List[CertificateResponseSchema]
    top_templates: List[Dict[str, Any]]
