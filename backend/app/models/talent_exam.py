"""
Talent Exam models for MEDHASAKTHI
Class-wise talent exams with centralized scheduling and management
"""
import uuid
from datetime import datetime, date
from enum import Enum
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer, 
    Float, JSON, ForeignKey, func, Index, Date, Time
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class ExamStatus(str, Enum):
    """Talent exam status"""
    SCHEDULED = "scheduled"
    REGISTRATION_OPEN = "registration_open"
    REGISTRATION_CLOSED = "registration_closed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    RESULTS_PUBLISHED = "results_published"
    CANCELLED = "cancelled"


class RegistrationStatus(str, Enum):
    """Student registration status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAYMENT_PENDING = "payment_pending"
    CANCELLED = "cancelled"
    DISQUALIFIED = "disqualified"


class ExamType(str, Enum):
    """Type of talent exam"""
    ANNUAL_TALENT = "annual_talent"
    OLYMPIAD = "olympiad"
    SCHOLARSHIP = "scholarship"
    APTITUDE = "aptitude"
    SUBJECT_MASTERY = "subject_mastery"
    COMPETITIVE = "competitive"


class ClassLevel(str, Enum):
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


class TalentExam(Base):
    """Centrally managed talent exams for different classes"""
    __tablename__ = "talent_exams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Exam identification
    exam_code = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    
    # Exam classification
    exam_type = Column(String(50), nullable=False, index=True)
    class_level = Column(String(20), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False, index=True)  # e.g., "2024-25"
    
    # Scheduling
    exam_date = Column(Date, nullable=False, index=True)
    exam_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Registration period
    registration_start_date = Column(DateTime(timezone=True), nullable=False)
    registration_end_date = Column(DateTime(timezone=True), nullable=False)
    
    # Exam configuration
    total_questions = Column(Integer, nullable=False)
    total_marks = Column(Integer, nullable=False)
    passing_marks = Column(Integer)
    negative_marking = Column(Boolean, default=False)
    negative_marks_per_question = Column(Float, default=0.0)
    
    # Subjects and syllabus
    subjects = Column(JSON)  # List of subjects with weightage
    syllabus_details = Column(JSON)  # Detailed syllabus information
    
    # Fees and eligibility
    registration_fee = Column(Float, default=0.0)
    eligibility_criteria = Column(JSON)  # Age, class, etc.
    
    # Exam settings
    is_proctored = Column(Boolean, default=True)
    allow_calculator = Column(Boolean, default=False)
    allow_rough_sheets = Column(Boolean, default=True)
    randomize_questions = Column(Boolean, default=True)
    
    # Results and certificates
    result_declaration_date = Column(Date)
    certificate_template_id = Column(UUID(as_uuid=True), ForeignKey("certificate_templates.id"))
    
    # Status and management
    status = Column(String(30), default=ExamStatus.SCHEDULED, index=True)
    is_active = Column(Boolean, default=True, index=True)
    max_registrations = Column(Integer)  # Optional limit
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    certificate_template = relationship("CertificateTemplate")
    registrations = relationship("TalentExamRegistration", back_populates="exam")
    sessions = relationship("TalentExamSession", back_populates="exam")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_talent_exam_class_year', 'class_level', 'academic_year'),
        Index('idx_talent_exam_date_status', 'exam_date', 'status'),
        Index('idx_talent_exam_registration_period', 'registration_start_date', 'registration_end_date'),
    )
    
    def __repr__(self):
        return f"<TalentExam(code={self.exam_code}, class={self.class_level}, date={self.exam_date})>"


class TalentExamRegistration(Base):
    """Student registrations for talent exams"""
    __tablename__ = "talent_exam_registrations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Registration identification
    registration_number = Column(String(50), unique=True, nullable=False, index=True)
    
    # Exam and student
    exam_id = Column(UUID(as_uuid=True), ForeignKey("talent_exams.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    
    # Registration details
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(30), default=RegistrationStatus.PENDING, index=True)
    
    # Student information (snapshot at registration)
    student_name = Column(String(200), nullable=False)
    student_email = Column(String(255))
    student_phone = Column(String(20))
    date_of_birth = Column(Date)
    current_class = Column(String(20))
    school_name = Column(String(300))
    
    # Parent/Guardian information
    parent_name = Column(String(200))
    parent_email = Column(String(255))
    parent_phone = Column(String(20))
    
    # Address information
    address = Column(JSON)  # Complete address details
    
    # Payment information
    registration_fee_paid = Column(Float, default=0.0)
    payment_status = Column(String(30), default="pending")
    payment_reference = Column(String(100))
    payment_date = Column(DateTime(timezone=True))
    
    # Exam center assignment
    exam_center_id = Column(UUID(as_uuid=True), ForeignKey("exam_centers.id"))
    seat_number = Column(String(20))
    
    # Special requirements
    special_requirements = Column(JSON)  # Disability accommodations, etc.
    
    # Verification
    documents_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verification_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exam = relationship("TalentExam", back_populates="registrations")
    student = relationship("Student")
    institute = relationship("Institute")
    exam_center = relationship("ExamCenter")
    verifier = relationship("User")
    session = relationship("TalentExamSession", back_populates="registration", uselist=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_registration_exam_student', 'exam_id', 'student_id'),
        Index('idx_registration_status_date', 'status', 'registration_date'),
        Index('idx_registration_institute', 'institute_id', 'exam_id'),
    )
    
    def __repr__(self):
        return f"<TalentExamRegistration(number={self.registration_number}, student={self.student_name})>"


class ExamCenter(Base):
    """Exam centers for conducting talent exams"""
    __tablename__ = "exam_centers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Center identification
    center_code = Column(String(20), unique=True, nullable=False, index=True)
    center_name = Column(String(300), nullable=False)
    
    # Location
    address = Column(JSON, nullable=False)  # Complete address
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False, index=True)
    pincode = Column(String(10), nullable=False)
    coordinates = Column(JSON)  # Latitude, longitude
    
    # Capacity and facilities
    total_capacity = Column(Integer, nullable=False)
    computer_labs = Column(Integer, default=0)
    regular_rooms = Column(Integer, default=0)
    facilities = Column(JSON)  # List of available facilities
    
    # Contact information
    contact_person = Column(String(200))
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    
    # Technical specifications
    internet_speed = Column(String(50))
    backup_power = Column(Boolean, default=False)
    cctv_enabled = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    registrations = relationship("TalentExamRegistration", back_populates="exam_center")
    
    def __repr__(self):
        return f"<ExamCenter(code={self.center_code}, name={self.center_name})>"


class TalentExamSession(Base):
    """Individual exam sessions for students"""
    __tablename__ = "talent_exam_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Session identification
    session_token = Column(String(100), unique=True, nullable=False, index=True)
    
    # Exam and registration
    exam_id = Column(UUID(as_uuid=True), ForeignKey("talent_exams.id"), nullable=False)
    registration_id = Column(UUID(as_uuid=True), ForeignKey("talent_exam_registrations.id"), nullable=False)
    
    # Session timing
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    
    # Exam progress
    current_question = Column(Integer, default=1)
    questions_attempted = Column(Integer, default=0)
    questions_answered = Column(Integer, default=0)
    
    # Responses and scoring
    responses = Column(JSON)  # Student responses to questions
    score = Column(Float)
    percentage = Column(Float)
    rank = Column(Integer)
    
    # Session status
    status = Column(String(30), default="not_started")  # not_started, in_progress, completed, terminated
    is_submitted = Column(Boolean, default=False)
    submission_time = Column(DateTime(timezone=True))
    
    # Proctoring data
    proctoring_data = Column(JSON)  # Screenshots, violations, etc.
    violations_count = Column(Integer, default=0)
    
    # Browser and device info
    browser_info = Column(JSON)
    device_info = Column(JSON)
    ip_address = Column(String(45))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exam = relationship("TalentExam", back_populates="sessions")
    registration = relationship("TalentExamRegistration", back_populates="session")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_exam_registration', 'exam_id', 'registration_id'),
        Index('idx_session_status_score', 'status', 'score'),
        Index('idx_session_timing', 'started_at', 'ended_at'),
    )
    
    def __repr__(self):
        return f"<TalentExamSession(token={self.session_token}, status={self.status})>"


class TalentExamNotification(Base):
    """Notifications for talent exams"""
    __tablename__ = "talent_exam_notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Notification details
    title = Column(String(300), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False, index=True)  # exam_scheduled, registration_open, etc.
    
    # Target audience
    exam_id = Column(UUID(as_uuid=True), ForeignKey("talent_exams.id"))
    target_class_levels = Column(JSON)  # List of class levels
    target_institutes = Column(JSON)  # List of institute IDs (optional)
    target_states = Column(JSON)  # List of states (optional)
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True))
    
    # Delivery channels
    send_email = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    send_push = Column(Boolean, default=True)
    send_in_app = Column(Boolean, default=True)
    
    # Status
    status = Column(String(30), default="scheduled")  # scheduled, sent, failed
    recipients_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exam = relationship("TalentExam")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<TalentExamNotification(title={self.title}, type={self.notification_type})>"
