"""
Talent Exam schemas for MEDHASAKTHI API
"""
from datetime import datetime, date, time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class ExamStatusEnum(str, Enum):
    """Talent exam status"""
    SCHEDULED = "scheduled"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    RESULTS_PUBLISHED = "results_published"
    CANCELLED = "cancelled"


class RegistrationStatusEnum(str, Enum):
    """Student registration status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAYMENT_PENDING = "payment_pending"
    CANCELLED = "cancelled"
    DISQUALIFIED = "disqualified"


class ExamTypeEnum(str, Enum):
    """Type of talent exam"""
    ANNUAL_TALENT = "annual_talent"
    OLYMPIAD = "olympiad"
    SCHOLARSHIP = "scholarship"
    APTITUDE = "aptitude"
    SUBJECT_MASTERY = "subject_mastery"
    COMPETITIVE = "competitive"


class ClassLevelEnum(str, Enum):
    """Class levels for talent exams"""
    CLASS_1 = "class_1"
    CLASS_2 = "class_2"
    CLASS_3 = "class_3"
    CLASS_4 = "class_4"
    CLASS_5 = "class_5"
    CLASS_6 = "class_6"
    CLASS_7 = "class_7"
    CLASS_8 = "class_8"
    CLASS_9 = "class_9"
    CLASS_10 = "class_10"
    CLASS_11 = "class_11"
    CLASS_12 = "class_12"


# Talent Exam Schemas
class TalentExamCreateSchema(BaseModel):
    """Schema for creating talent exams"""
    exam_code: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    exam_type: ExamTypeEnum
    class_level: ClassLevelEnum
    academic_year: str = Field(..., min_length=7, max_length=20)  # e.g., "2024-25"
    exam_date: date
    exam_time: time
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    registration_start_date: datetime
    registration_end_date: datetime
    total_questions: int = Field(..., gt=0, le=500)
    total_marks: int = Field(..., gt=0)
    passing_marks: Optional[int] = None
    negative_marking: bool = False
    negative_marks_per_question: float = Field(default=0.0, ge=0.0)
    subjects: List[Dict[str, Any]] = Field(default_factory=list)
    syllabus_details: Optional[Dict[str, Any]] = None
    registration_fee: float = Field(default=0.0, ge=0.0)
    eligibility_criteria: Optional[Dict[str, Any]] = None
    is_proctored: bool = True
    allow_calculator: bool = False
    allow_rough_sheets: bool = True
    randomize_questions: bool = True
    result_declaration_date: Optional[date] = None
    certificate_template_id: Optional[str] = None
    max_registrations: Optional[int] = None

    @validator('registration_end_date')
    def validate_registration_dates(cls, v, values):
        if 'registration_start_date' in values and v <= values['registration_start_date']:
            raise ValueError('Registration end date must be after start date')
        return v

    @validator('exam_date')
    def validate_exam_date(cls, v, values):
        if 'registration_end_date' in values and v <= values['registration_end_date'].date():
            raise ValueError('Exam date must be after registration end date')
        return v


class TalentExamUpdateSchema(BaseModel):
    """Schema for updating talent exams"""
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    exam_date: Optional[date] = None
    exam_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, gt=0, le=480)
    registration_start_date: Optional[datetime] = None
    registration_end_date: Optional[datetime] = None
    total_questions: Optional[int] = Field(None, gt=0, le=500)
    total_marks: Optional[int] = Field(None, gt=0)
    passing_marks: Optional[int] = None
    negative_marking: Optional[bool] = None
    negative_marks_per_question: Optional[float] = Field(None, ge=0.0)
    subjects: Optional[List[Dict[str, Any]]] = None
    syllabus_details: Optional[Dict[str, Any]] = None
    registration_fee: Optional[float] = Field(None, ge=0.0)
    eligibility_criteria: Optional[Dict[str, Any]] = None
    is_proctored: Optional[bool] = None
    allow_calculator: Optional[bool] = None
    allow_rough_sheets: Optional[bool] = None
    randomize_questions: Optional[bool] = None
    result_declaration_date: Optional[date] = None
    status: Optional[ExamStatusEnum] = None
    max_registrations: Optional[int] = None


class TalentExamResponseSchema(BaseModel):
    """Schema for talent exam response"""
    id: str
    exam_code: str
    title: str
    description: Optional[str]
    exam_type: str
    class_level: str
    academic_year: str
    exam_date: date
    exam_time: time
    duration_minutes: int
    registration_start_date: datetime
    registration_end_date: datetime
    total_questions: int
    total_marks: int
    passing_marks: Optional[int]
    negative_marking: bool
    negative_marks_per_question: float
    subjects: List[Dict[str, Any]]
    syllabus_details: Optional[Dict[str, Any]]
    registration_fee: float
    eligibility_criteria: Optional[Dict[str, Any]]
    is_proctored: bool
    allow_calculator: bool
    allow_rough_sheets: bool
    randomize_questions: bool
    result_declaration_date: Optional[date]
    certificate_template_id: Optional[str]
    status: str
    is_active: bool
    max_registrations: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    registration_count: Optional[int] = None
    is_registration_open: Optional[bool] = None
    days_until_exam: Optional[int] = None
    
    class Config:
        from_attributes = True


# Registration Schemas
class TalentExamRegistrationCreateSchema(BaseModel):
    """Schema for creating talent exam registration"""
    exam_id: str
    student_name: str = Field(..., min_length=1, max_length=200)
    student_email: Optional[EmailStr] = None
    student_phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: date
    current_class: str = Field(..., max_length=20)
    school_name: str = Field(..., min_length=1, max_length=300)
    parent_name: str = Field(..., min_length=1, max_length=200)
    parent_email: EmailStr
    parent_phone: str = Field(..., max_length=20)
    address: Dict[str, Any]
    special_requirements: Optional[Dict[str, Any]] = None


class TalentExamRegistrationUpdateSchema(BaseModel):
    """Schema for updating talent exam registration"""
    student_name: Optional[str] = Field(None, min_length=1, max_length=200)
    student_email: Optional[EmailStr] = None
    student_phone: Optional[str] = Field(None, max_length=20)
    parent_name: Optional[str] = Field(None, min_length=1, max_length=200)
    parent_email: Optional[EmailStr] = None
    parent_phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Dict[str, Any]] = None
    special_requirements: Optional[Dict[str, Any]] = None
    status: Optional[RegistrationStatusEnum] = None
    exam_center_id: Optional[str] = None
    seat_number: Optional[str] = None
    documents_verified: Optional[bool] = None


class TalentExamRegistrationResponseSchema(BaseModel):
    """Schema for talent exam registration response"""
    id: str
    registration_number: str
    exam_id: str
    student_id: str
    institute_id: str
    registration_date: datetime
    status: str
    student_name: str
    student_email: Optional[str]
    student_phone: Optional[str]
    date_of_birth: date
    current_class: str
    school_name: str
    parent_name: str
    parent_email: str
    parent_phone: str
    address: Dict[str, Any]
    registration_fee_paid: float
    payment_status: str
    payment_reference: Optional[str]
    payment_date: Optional[datetime]
    exam_center_id: Optional[str]
    seat_number: Optional[str]
    special_requirements: Optional[Dict[str, Any]]
    documents_verified: bool
    verification_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Related data
    exam_title: Optional[str] = None
    exam_date: Optional[date] = None
    exam_center_name: Optional[str] = None
    
    class Config:
        from_attributes = True


# Exam Center Schemas
class ExamCenterCreateSchema(BaseModel):
    """Schema for creating exam centers"""
    center_code: str = Field(..., min_length=1, max_length=20)
    center_name: str = Field(..., min_length=1, max_length=300)
    address: Dict[str, Any]
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    pincode: str = Field(..., min_length=6, max_length=10)
    coordinates: Optional[Dict[str, float]] = None
    total_capacity: int = Field(..., gt=0)
    computer_labs: int = Field(default=0, ge=0)
    regular_rooms: int = Field(default=0, ge=0)
    facilities: List[str] = Field(default_factory=list)
    contact_person: Optional[str] = Field(None, max_length=200)
    contact_phone: Optional[str] = Field(None, max_length=20)
    contact_email: Optional[EmailStr] = None
    internet_speed: Optional[str] = Field(None, max_length=50)
    backup_power: bool = False
    cctv_enabled: bool = False


class ExamCenterResponseSchema(BaseModel):
    """Schema for exam center response"""
    id: str
    center_code: str
    center_name: str
    address: Dict[str, Any]
    city: str
    state: str
    pincode: str
    coordinates: Optional[Dict[str, float]]
    total_capacity: int
    computer_labs: int
    regular_rooms: int
    facilities: List[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    internet_speed: Optional[str]
    backup_power: bool
    cctv_enabled: bool
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    current_bookings: Optional[int] = None
    available_capacity: Optional[int] = None
    
    class Config:
        from_attributes = True


# Search and Filter Schemas
class TalentExamSearchSchema(BaseModel):
    """Schema for talent exam search"""
    query: Optional[str] = None
    exam_type: Optional[ExamTypeEnum] = None
    class_level: Optional[ClassLevelEnum] = None
    academic_year: Optional[str] = None
    status: Optional[ExamStatusEnum] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    city: Optional[str] = None
    state: Optional[str] = None
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)


class TalentExamSearchResponseSchema(BaseModel):
    """Schema for talent exam search response"""
    exams: List[TalentExamResponseSchema]
    total: int
    page: int
    limit: int
    total_pages: int


# Notification Schemas
class TalentExamNotificationCreateSchema(BaseModel):
    """Schema for creating talent exam notifications"""
    title: str = Field(..., min_length=1, max_length=300)
    message: str = Field(..., min_length=1)
    notification_type: str = Field(..., min_length=1, max_length=50)
    exam_id: Optional[str] = None
    target_class_levels: List[ClassLevelEnum] = Field(default_factory=list)
    target_institutes: Optional[List[str]] = None
    target_states: Optional[List[str]] = None
    scheduled_at: datetime
    send_email: bool = True
    send_sms: bool = False
    send_push: bool = True
    send_in_app: bool = True


class TalentExamNotificationResponseSchema(BaseModel):
    """Schema for talent exam notification response"""
    id: str
    title: str
    message: str
    notification_type: str
    exam_id: Optional[str]
    target_class_levels: List[str]
    target_institutes: Optional[List[str]]
    target_states: Optional[List[str]]
    scheduled_at: datetime
    sent_at: Optional[datetime]
    send_email: bool
    send_sms: bool
    send_push: bool
    send_in_app: bool
    status: str
    recipients_count: int
    delivered_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analytics Schemas
class TalentExamStatsSchema(BaseModel):
    """Schema for talent exam statistics"""
    total_exams: int
    exams_by_status: Dict[str, int]
    exams_by_class: Dict[str, int]
    exams_by_type: Dict[str, int]
    total_registrations: int
    registrations_by_status: Dict[str, int]
    upcoming_exams: List[TalentExamResponseSchema]
    recent_results: List[Dict[str, Any]]


class RegistrationAnalyticsSchema(BaseModel):
    """Schema for registration analytics"""
    exam_id: str
    exam_title: str
    total_registrations: int
    registrations_by_state: Dict[str, int]
    registrations_by_institute_type: Dict[str, int]
    daily_registrations: List[Dict[str, Any]]
    payment_statistics: Dict[str, Any]
    top_performing_centers: List[Dict[str, Any]]
