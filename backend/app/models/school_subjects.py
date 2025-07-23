"""
School Subject Management Models for MEDHASAKTHI
Comprehensive class-wise subject structure for different education boards
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class EducationBoard(enum.Enum):
    CBSE = "cbse"
    ICSE = "icse"
    STATE_BOARD = "state_board"
    IB = "ib"
    CAMBRIDGE = "cambridge"
    NIOS = "nios"


class ClassLevel(enum.Enum):
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


class SubjectCategory(enum.Enum):
    CORE = "core"
    ELECTIVE = "elective"
    OPTIONAL = "optional"
    LANGUAGE = "language"
    VOCATIONAL = "vocational"
    ACTIVITY = "activity"


class Subject(Base):
    """Subject master table with board-specific configurations"""
    __tablename__ = "subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(Text)
    category = Column(Enum(SubjectCategory), nullable=False)
    
    # Subject metadata
    is_core_subject = Column(Boolean, default=False)
    is_language = Column(Boolean, default=False)
    requires_practical = Column(Boolean, default=False)
    
    # Grading configuration
    theory_marks = Column(Integer, default=100)
    practical_marks = Column(Integer, default=0)
    internal_assessment_marks = Column(Integer, default=0)
    
    # Additional metadata
    subject_icon = Column(String(100))  # Icon class or URL
    subject_color = Column(String(7))   # Hex color code
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    board_subjects = relationship("BoardSubject", back_populates="subject")
    class_subjects = relationship("ClassSubject", back_populates="subject")


class BoardSubject(Base):
    """Subject configuration for specific education boards"""
    __tablename__ = "board_subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    board = Column(Enum(EducationBoard), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    
    # Board-specific configuration
    board_subject_code = Column(String(20))  # Board's internal code
    board_subject_name = Column(String(200))  # Board's official name
    is_compulsory = Column(Boolean, default=False)
    
    # Grading scheme
    grading_scheme = Column(JSON)  # Board-specific grading configuration
    passing_marks = Column(Integer, default=35)
    
    # Syllabus information
    syllabus_url = Column(String(500))
    syllabus_version = Column(String(50))
    last_updated = Column(DateTime(timezone=True))
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="board_subjects")


class ClassSubject(Base):
    """Subject allocation for specific classes"""
    __tablename__ = "class_subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_level = Column(Enum(ClassLevel), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    board = Column(Enum(EducationBoard), nullable=False)
    
    # Class-specific configuration
    is_mandatory = Column(Boolean, default=True)
    weekly_periods = Column(Integer, default=5)
    annual_hours = Column(Integer, default=180)
    
    # Assessment configuration
    assessment_pattern = Column(JSON)  # Class-specific assessment details
    project_required = Column(Boolean, default=False)
    lab_required = Column(Boolean, default=False)
    
    # Prerequisites and progression
    prerequisites = Column(JSON)  # Required previous subjects/classes
    leads_to = Column(JSON)       # Next level subjects
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subject = relationship("Subject", back_populates="class_subjects")
    chapters = relationship("SubjectChapter", back_populates="class_subject")


class SubjectChapter(Base):
    """Chapter/topic structure for subjects"""
    __tablename__ = "subject_chapters"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_subject_id = Column(UUID(as_uuid=True), ForeignKey("class_subjects.id"), nullable=False)
    
    # Chapter information
    chapter_number = Column(Integer, nullable=False)
    chapter_name = Column(String(300), nullable=False)
    chapter_description = Column(Text)
    
    # Learning objectives
    learning_objectives = Column(JSON)  # List of learning outcomes
    key_concepts = Column(JSON)         # Important concepts covered
    
    # Time allocation
    estimated_hours = Column(Integer, default=10)
    difficulty_level = Column(String(20), default="medium")
    
    # Resources
    reference_materials = Column(JSON)  # Books, videos, etc.
    practice_questions_count = Column(Integer, default=0)
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    class_subject = relationship("ClassSubject", back_populates="chapters")
    topics = relationship("ChapterTopic", back_populates="chapter")


class ChapterTopic(Base):
    """Detailed topics within chapters"""
    __tablename__ = "chapter_topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chapter_id = Column(UUID(as_uuid=True), ForeignKey("subject_chapters.id"), nullable=False)
    
    # Topic information
    topic_number = Column(Integer, nullable=False)
    topic_name = Column(String(300), nullable=False)
    topic_description = Column(Text)
    
    # Content details
    content_type = Column(String(50))  # theory, practical, project, etc.
    estimated_time_minutes = Column(Integer, default=45)
    
    # Learning resources
    video_links = Column(JSON)
    reading_materials = Column(JSON)
    practice_exercises = Column(JSON)
    
    # Assessment
    assessment_weightage = Column(Integer, default=5)  # Percentage in exams
    question_types = Column(JSON)  # MCQ, descriptive, numerical, etc.
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chapter = relationship("SubjectChapter", back_populates="topics")


class SubjectTeacher(Base):
    """Teacher assignment to subjects"""
    __tablename__ = "subject_teachers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"), nullable=False)
    
    # Assignment details
    class_levels = Column(JSON)  # Classes this teacher handles for this subject
    academic_year = Column(String(10), nullable=False)
    
    # Teaching load
    weekly_periods = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    
    # Qualifications
    qualification = Column(String(200))
    experience_years = Column(Integer, default=0)
    specialization = Column(String(200))
    
    # Performance metrics
    student_feedback_score = Column(Integer, default=0)  # Out of 5
    completion_rate = Column(Integer, default=0)  # Syllabus completion %
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StudentSubject(Base):
    """Student enrollment in subjects"""
    __tablename__ = "student_subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    class_subject_id = Column(UUID(as_uuid=True), ForeignKey("class_subjects.id"), nullable=False)
    
    # Enrollment details
    academic_year = Column(String(10), nullable=False)
    enrollment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Subject selection (for electives)
    is_elective = Column(Boolean, default=False)
    selection_reason = Column(Text)
    
    # Performance tracking
    current_grade = Column(String(5))
    attendance_percentage = Column(Integer, default=0)
    assignment_completion = Column(Integer, default=0)
    
    # Progress tracking
    chapters_completed = Column(JSON)  # List of completed chapter IDs
    topics_mastered = Column(JSON)     # List of mastered topic IDs
    weak_areas = Column(JSON)          # Areas needing improvement
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SubjectAssessment(Base):
    """Assessment configuration for subjects"""
    __tablename__ = "subject_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    class_subject_id = Column(UUID(as_uuid=True), ForeignKey("class_subjects.id"), nullable=False)
    
    # Assessment details
    assessment_name = Column(String(200), nullable=False)
    assessment_type = Column(String(50), nullable=False)  # unit_test, mid_term, final, project
    
    # Weightage and marks
    total_marks = Column(Integer, nullable=False)
    weightage_percentage = Column(Integer, nullable=False)
    passing_marks = Column(Integer, nullable=False)
    
    # Timing
    duration_minutes = Column(Integer, default=180)
    scheduled_date = Column(DateTime(timezone=True))
    
    # Question configuration
    question_distribution = Column(JSON)  # MCQ, short, long answer distribution
    chapter_weightage = Column(JSON)      # Marks distribution across chapters
    
    # Audit fields
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
