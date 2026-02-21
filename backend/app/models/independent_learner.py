"""
Independent Learner Models for MEDHASAKTHI
For individuals registering outside of institutions
"""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Text, JSON, Enum as SQLEnum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class Gender(str, Enum):
    """Gender options"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class LearnerCategory(str, Enum):
    """Categories for independent learners"""
    SCHOOL_STUDENT = "school_student"  # K-12 students not in registered institutes
    COLLEGE_STUDENT = "college_student"  # Higher education students
    WORKING_PROFESSIONAL = "working_professional"  # Employed individuals
    JOB_SEEKER = "job_seeker"  # Unemployed seeking certifications
    ENTREPRENEUR = "entrepreneur"  # Business owners
    FREELANCER = "freelancer"  # Independent contractors
    RETIRED = "retired"  # Retired individuals
    HOMEMAKER = "homemaker"  # Stay-at-home individuals
    OTHER = "other"  # Other categories


class EducationLevel(str, Enum):
    """Education levels for independent learners"""
    BELOW_10TH = "below_10th"
    CLASS_10TH = "class_10th"
    CLASS_12TH = "class_12th"
    DIPLOMA = "diploma"
    UNDERGRADUATE = "undergraduate"
    POSTGRADUATE = "postgraduate"
    DOCTORATE = "doctorate"
    PROFESSIONAL = "professional"


class IndependentLearner(Base):
    """Independent learner profile for non-institutional users"""
    __tablename__ = "independent_learners"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Learner Identification
    learner_id = Column(String(50), unique=True, nullable=False, index=True)  # Auto-generated
    
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date)
    gender = Column(SQLEnum(Gender))
    nationality = Column(String(50))
    
    # Contact Information
    phone = Column(String(20), nullable=False)
    alternate_phone = Column(String(20))
    address_line1 = Column(String(200))
    address_line2 = Column(String(200))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Professional Information
    category = Column(SQLEnum(LearnerCategory), nullable=False)
    education_level = Column(SQLEnum(EducationLevel), nullable=False)
    current_occupation = Column(String(200))
    organization_name = Column(String(200))
    work_experience_years = Column(Integer, default=0)
    annual_income_range = Column(String(50))  # e.g., "0-3L", "3-5L", "5-10L", etc.
    
    # Educational Background
    highest_qualification = Column(String(200))
    specialization = Column(String(200))
    university_college = Column(String(200))
    graduation_year = Column(Integer)
    percentage_cgpa = Column(String(20))
    
    # Learning Preferences
    preferred_subjects = Column(JSON)  # Array of subjects interested in
    learning_goals = Column(Text)  # What they want to achieve
    preferred_exam_types = Column(JSON)  # Types of exams they're interested in
    study_time_availability = Column(String(50))  # Hours per week
    preferred_language = Column(String(50), default="English")
    
    # Verification Documents
    id_proof_type = Column(String(50))  # Aadhar, Passport, etc.
    id_proof_number = Column(String(100))
    id_proof_verified = Column(Boolean, default=False)
    address_proof_type = Column(String(50))
    address_proof_verified = Column(Boolean, default=False)
    education_proof_verified = Column(Boolean, default=False)
    
    # Account Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_level = Column(String(20), default="basic")  # basic, standard, premium
    kyc_completed = Column(Boolean, default=False)
    
    # Subscription & Payment
    subscription_type = Column(String(50), default="free")  # free, basic, premium, enterprise
    subscription_start_date = Column(Date)
    subscription_end_date = Column(Date)
    payment_method = Column(String(50))
    
    # Referral Information
    referral_code = Column(String(20), unique=True)  # Their referral code
    referred_by_code = Column(String(20))  # Who referred them
    referral_bonus_earned = Column(Numeric(10, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="independent_learner_profile")
    exam_registrations = relationship("IndependentExamRegistration", back_populates="learner")
    certificates = relationship("IndependentCertificate", back_populates="learner")
    payments = relationship("IndependentPayment", back_populates="learner")
    
    def __repr__(self):
        return f"<IndependentLearner {self.learner_id}: {self.first_name} {self.last_name}>"


class CertificationProgram(Base):
    """Certification programs available for independent learners"""
    __tablename__ = "certification_programs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Program Information
    program_code = Column(String(50), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    detailed_syllabus = Column(Text)
    
    # Program Classification
    category = Column(String(100))  # IT, Finance, Marketing, etc.
    subcategory = Column(String(100))  # Web Development, Data Science, etc.
    level = Column(String(50))  # Beginner, Intermediate, Advanced
    duration_hours = Column(Integer)  # Expected study hours
    validity_months = Column(Integer, default=24)  # Certificate validity
    
    # Eligibility Criteria
    min_education_level = Column(SQLEnum(EducationLevel))
    min_age = Column(Integer, default=16)
    max_age = Column(Integer)
    prerequisites = Column(JSON)  # Array of prerequisite skills/certifications
    target_audience = Column(JSON)  # Array of target learner categories
    
    # Pricing Configuration
    base_price = Column(Numeric(10, 2), nullable=False)
    discounted_price = Column(Numeric(10, 2))
    currency = Column(String(10), default="INR")
    
    # Category-based Pricing
    pricing_tiers = Column(JSON)  # Different prices for different learner categories
    bulk_discount_config = Column(JSON)  # Bulk purchase discounts
    referral_discount_percent = Column(Integer, default=0)
    
    # Exam Configuration
    total_questions = Column(Integer, default=100)
    exam_duration_minutes = Column(Integer, default=120)
    passing_percentage = Column(Integer, default=70)
    max_attempts = Column(Integer, default=3)
    retake_fee = Column(Numeric(10, 2))
    
    # Content & Resources
    study_materials = Column(JSON)  # Links to study resources
    practice_tests_count = Column(Integer, default=5)
    video_lectures_hours = Column(Integer, default=0)
    downloadable_resources = Column(JSON)
    
    # Program Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    enrollment_start_date = Column(Date)
    enrollment_end_date = Column(Date)
    
    # Statistics
    total_enrollments = Column(Integer, default=0)
    total_certifications = Column(Integer, default=0)
    average_score = Column(Numeric(5, 2), default=0)
    success_rate = Column(Numeric(5, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    registrations = relationship("IndependentExamRegistration", back_populates="program")
    certificates = relationship("IndependentCertificate", back_populates="program")
    
    def __repr__(self):
        return f"<CertificationProgram {self.program_code}: {self.title}>"


class IndependentExamRegistration(Base):
    """Exam registrations for independent learners"""
    __tablename__ = "independent_exam_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id = Column(UUID(as_uuid=True), ForeignKey("independent_learners.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("certification_programs.id"), nullable=False)
    
    # Registration Information
    registration_number = Column(String(50), unique=True, nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    exam_date = Column(Date)
    exam_time = Column(String(20))
    exam_center = Column(String(200), default="Online")
    
    # Payment Information
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), default="pending")  # pending, paid, failed, refunded
    payment_method = Column(String(50))
    transaction_id = Column(String(100))
    payment_date = Column(DateTime(timezone=True))
    
    # Exam Status
    status = Column(String(20), default="registered")  # registered, appeared, passed, failed, cancelled
    attempt_number = Column(Integer, default=1)
    exam_started_at = Column(DateTime(timezone=True))
    exam_completed_at = Column(DateTime(timezone=True))
    
    # Results
    score_obtained = Column(Integer)
    total_score = Column(Integer)
    percentage = Column(Numeric(5, 2))
    result = Column(String(20))  # pass, fail
    grade = Column(String(10))  # A+, A, B+, B, C, F
    
    # Proctoring Information
    proctoring_enabled = Column(Boolean, default=True)
    proctoring_violations = Column(JSON)  # Array of violation records
    proctoring_score = Column(Integer)  # Integrity score out of 100
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    learner = relationship("IndependentLearner", back_populates="exam_registrations")
    program = relationship("CertificationProgram", back_populates="registrations")
    certificate = relationship("IndependentCertificate", back_populates="registration", uselist=False)
    
    def __repr__(self):
        return f"<IndependentExamRegistration {self.registration_number}>"


class IndependentCertificate(Base):
    """Certificates issued to independent learners"""
    __tablename__ = "independent_certificates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id = Column(UUID(as_uuid=True), ForeignKey("independent_learners.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("certification_programs.id"), nullable=False)
    registration_id = Column(UUID(as_uuid=True), ForeignKey("independent_exam_registrations.id"), nullable=False)
    
    # Certificate Information
    certificate_number = Column(String(50), unique=True, nullable=False)
    issue_date = Column(Date, nullable=False)
    expiry_date = Column(Date)
    
    # Certificate Details
    learner_name = Column(String(200), nullable=False)
    program_title = Column(String(200), nullable=False)
    score_achieved = Column(Integer)
    grade_obtained = Column(String(10))
    
    # Verification
    verification_code = Column(String(100), unique=True, nullable=False)
    blockchain_hash = Column(String(256))  # For blockchain verification
    is_verified = Column(Boolean, default=True)
    
    # Digital Certificate
    certificate_url = Column(String(500))  # URL to download certificate
    certificate_template = Column(String(100))  # Template used
    digital_signature = Column(Text)  # Digital signature for authenticity
    
    # Status
    status = Column(String(20), default="active")  # active, revoked, expired
    revocation_reason = Column(String(200))
    revoked_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    learner = relationship("IndependentLearner", back_populates="certificates")
    program = relationship("CertificationProgram", back_populates="certificates")
    registration = relationship("IndependentExamRegistration", back_populates="certificate")
    
    def __repr__(self):
        return f"<IndependentCertificate {self.certificate_number}>"


class IndependentPayment(Base):
    """Payment records for independent learners"""
    __tablename__ = "independent_payments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id = Column(UUID(as_uuid=True), ForeignKey("independent_learners.id"), nullable=False)
    
    # Payment Information
    payment_id = Column(String(100), unique=True, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR")
    payment_type = Column(String(50))  # exam_fee, subscription, retake_fee, etc.
    
    # Payment Gateway Details
    gateway = Column(String(50))  # razorpay, stripe, paypal, etc.
    gateway_transaction_id = Column(String(200))
    gateway_payment_id = Column(String(200))
    gateway_order_id = Column(String(200))
    
    # Payment Status
    status = Column(String(20), default="pending")  # pending, success, failed, refunded
    payment_method = Column(String(50))  # card, upi, netbanking, wallet, etc.
    
    # Billing Information
    billing_name = Column(String(200))
    billing_email = Column(String(200))
    billing_phone = Column(String(20))
    billing_address = Column(JSON)
    
    # Transaction Details
    initiated_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    failure_reason = Column(String(500))
    
    # Refund Information
    refund_amount = Column(Numeric(10, 2))
    refund_status = Column(String(20))  # pending, processed, failed
    refund_reason = Column(String(500))
    refunded_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    learner = relationship("IndependentLearner", back_populates="payments")
    
    def __repr__(self):
        return f"<IndependentPayment {self.payment_id}: {self.amount} {self.currency}>"
