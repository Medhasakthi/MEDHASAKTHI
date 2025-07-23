"""
User-related database models
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


# Create __init__.py files for models
def create_init_files():
    """Helper function to create __init__.py files"""
    pass


class UserRole(str, Enum):
    """User roles in the system"""
    SUPER_ADMIN = "super_admin"
    INSTITUTE_ADMIN = "institute_admin"
    TEACHER = "teacher"
    STUDENT = "student"
    PARENT = "parent"


class SubscriptionPlan(str, Enum):
    """Subscription plans for institutes"""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class User(Base):
    """Main user table for authentication"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, index=True)
    
    # Account status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False, index=True)
    is_suspended = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Security
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    password_changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Two-factor authentication
    totp_secret = Column(String(32))
    is_2fa_enabled = Column(Boolean, default=False)
    backup_codes = Column(Text)  # JSON array of backup codes
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    security_logs = relationship("SecurityLog", back_populates="user", cascade="all, delete-orphan")
    device_sessions = relationship("DeviceSession", back_populates="user", cascade="all, delete-orphan")
    independent_learner_profile = relationship("IndependentLearner", back_populates="user", uselist=False, cascade="all, delete-orphan")

    # Load balancer relationships
    added_servers = relationship("Server", foreign_keys="Server.added_by", back_populates="added_by_user")
    removed_servers = relationship("Server", foreign_keys="Server.removed_by", back_populates="removed_by_user")
    load_balancer_configs = relationship("LoadBalancerConfig", back_populates="created_by_user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserProfile(Base):
    """Extended user profile information"""
    __tablename__ = "user_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Personal information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    gender = Column(String(10))
    
    # Contact information
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))
    
    # Profile
    profile_picture_url = Column(String(500))
    bio = Column(Text)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, name={self.full_name})>"


class InstituteType(str, Enum):
    """Types of educational institutes"""
    SCHOOL = "school"
    PRIMARY_SCHOOL = "primary_school"
    SECONDARY_SCHOOL = "secondary_school"
    HIGHER_SECONDARY_SCHOOL = "higher_secondary_school"
    COLLEGE = "college"
    UNIVERSITY = "university"
    COACHING_CENTER = "coaching_center"
    TRAINING_INSTITUTE = "training_institute"
    RESEARCH_INSTITUTE = "research_institute"


class Institute(Base):
    """Educational institutes/organizations"""
    __tablename__ = "institutes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)

    # Admin
    admin_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Institute classification
    institute_type = Column(String(50), nullable=False, index=True)
    education_level = Column(String(50))  # primary, secondary, higher_secondary, higher_education

    # School-specific fields
    education_board = Column(String(50))  # CBSE, ICSE, State boards
    medium_of_instruction = Column(JSON)  # List of languages
    classes_offered = Column(JSON)  # List of class levels offered
    streams_offered = Column(JSON)  # Science, Commerce, Arts (for higher secondary)

    # Institute details
    description = Column(Text)
    website = Column(String(255))
    phone = Column(String(20))
    email = Column(String(255))

    # School registration details
    school_registration_number = Column(String(100))
    affiliation_number = Column(String(100))
    recognition_status = Column(String(50))  # recognized, provisional, etc.
    establishment_year = Column(Integer)
    
    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))
    postal_code = Column(String(20))

    # School infrastructure
    total_students = Column(Integer, default=0)
    total_teachers = Column(Integer, default=0)
    total_classrooms = Column(Integer, default=0)
    has_library = Column(Boolean, default=False)
    has_laboratory = Column(Boolean, default=False)
    has_computer_lab = Column(Boolean, default=False)
    has_playground = Column(Boolean, default=False)

    # Facilities and amenities
    facilities = Column(JSON)  # List of available facilities
    transport_facility = Column(Boolean, default=False)
    hostel_facility = Column(Boolean, default=False)
    canteen_facility = Column(Boolean, default=False)

    # Academic information
    academic_calendar = Column(JSON)  # Academic year structure
    examination_pattern = Column(JSON)  # How exams are conducted
    grading_system = Column(String(50))  # Grading system used

    # Contact information
    principal_name = Column(String(200))
    principal_email = Column(String(255))
    principal_phone = Column(String(20))
    contact_person_name = Column(String(200))
    contact_person_designation = Column(String(100))

    # Subscription
    subscription_plan = Column(String(50), default=SubscriptionPlan.FREE)
    subscription_expires_at = Column(DateTime(timezone=True))
    max_students = Column(Integer, default=100)
    max_teachers = Column(Integer, default=10)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    admin = relationship("User", foreign_keys=[admin_user_id])
    students = relationship("Student", back_populates="institute", cascade="all, delete-orphan")
    teachers = relationship("Teacher", back_populates="institute", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Institute(id={self.id}, name={self.name}, code={self.code})>"


class Student(Base):
    """Student-specific information"""
    __tablename__ = "students"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    
    # Student identification
    student_id = Column(String(50), nullable=False, index=True)  # Institute-specific ID
    roll_number = Column(String(50))
    
    # Academic information
    class_level = Column(String(20), index=True)  # class_1, class_2, etc.
    section = Column(String(10))  # A, B, C, etc.
    academic_year = Column(String(20), index=True)  # 2024-25
    admission_number = Column(String(50))

    # School-specific information
    education_board = Column(String(50))  # CBSE, ICSE, State board
    medium_of_instruction = Column(String(50))  # English, Hindi, etc.
    stream = Column(String(30))  # Science, Commerce, Arts (for Class 11-12)

    # Academic progression
    previous_class = Column(String(20))
    promotion_status = Column(String(30))  # promoted, detained, etc.
    subjects_enrolled = Column(JSON)  # List of subjects student is enrolled in

    # Performance tracking
    current_grade = Column(String(10))  # A+, A, B+, etc.
    current_percentage = Column(Float)
    attendance_percentage = Column(Float, default=0.0)

    # Additional academic details
    house = Column(String(50))  # School house system
    transport_required = Column(Boolean, default=False)
    hostel_required = Column(Boolean, default=False)
    special_needs = Column(JSON)  # Any special educational needs
    
    # Parent/Guardian
    parent_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    
    # Academic status
    enrollment_date = Column(Date, default=func.current_date())
    graduation_date = Column(Date)
    is_active = Column(Boolean, default=True, index=True)

    # Performance tracking
    total_exams_taken = Column(Integer, default=0)
    average_score = Column(Integer, default=0)  # Percentage

    # Institutional management fields
    auto_generated_email = Column(String(255))  # studentid@institutename.com
    default_password_changed = Column(Boolean, default=False)
    first_login_completed = Column(Boolean, default=False)
    password_reset_required = Column(Boolean, default=True)  # Force password change on first login
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    institute = relationship("Institute", back_populates="students")
    parent = relationship("User", foreign_keys=[parent_user_id])
    
    def __repr__(self):
        return f"<Student(id={self.id}, student_id={self.student_id}, institute={self.institute_id})>"


class Teacher(Base):
    """Teacher-specific information"""
    __tablename__ = "teachers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    
    # Teacher identification
    teacher_id = Column(String(50), nullable=False, index=True)  # Institute-specific teacher ID
    employee_id = Column(String(50), nullable=False, index=True)

    # Professional information
    subjects = Column(Text)  # JSON array of subjects
    qualifications = Column(Text)  # JSON array of qualifications
    subject_specialization = Column(String(200))  # Primary subject
    experience_years = Column(Integer, default=0)
    designation = Column(String(100))  # Senior Teacher, HOD, Principal, etc.
    department = Column(String(100))

    # Contact
    office_phone = Column(String(20))
    office_location = Column(String(100))
    phone = Column(String(15))
    address = Column(Text)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(15))

    # Personal Information
    date_of_birth = Column(Date)
    gender = Column(String(20))  # Will be updated to use Gender enum later
    blood_group = Column(String(5))
    aadhar_number = Column(String(20))
    pan_number = Column(String(15))

    # Teaching Assignment
    classes_assigned = Column(JSON)  # List of classes teacher handles
    subjects_assigned = Column(JSON)  # List of subjects teacher teaches
    is_class_teacher = Column(Boolean, default=False)
    class_teacher_of = Column(String(50))  # Class for which teacher is class teacher

    # Institutional management fields
    auto_generated_email = Column(String(255))  # teacherid@institutename.com
    default_password_changed = Column(Boolean, default=False)
    first_login_completed = Column(Boolean, default=False)
    password_reset_required = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    joining_date = Column(Date, default=func.current_date())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    institute = relationship("Institute", back_populates="teachers")
    
    def __repr__(self):
        return f"<Teacher(id={self.id}, employee_id={self.employee_id}, institute={self.institute_id})>"


class SecurityLog(Base):
    """Security audit log for tracking security events"""
    __tablename__ = "security_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    details = Column(Text, nullable=True)  # Encrypted JSON details
    severity = Column(String(20), nullable=False, index=True)  # INFO, WARNING, ERROR, CRITICAL
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    user = relationship("User", back_populates="security_logs")


class DeviceSession(Base):
    """Device session tracking for enhanced security"""
    __tablename__ = "device_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    device_fingerprint = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    location_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="device_sessions")


class UserSession(Base):
    """User session tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session information
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False)
    
    # Device and location
    device_info = Column(Text)  # JSON with device details
    user_agent = Column(Text)
    ip_address = Column(INET)
    location = Column(String(100))  # City, Country
    
    # Session status
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, active={self.is_active})>"


class PasswordResetToken(Base):
    """Password reset tokens"""
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True))
    
    # Security
    ip_address = Column(INET)
    user_agent = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.used})>"


class EmailVerificationToken(Base):
    """Email verification tokens"""
    __tablename__ = "email_verification_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    used_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id}, used={self.used})>"
