"""
School Education models for MEDHASAKTHI
Comprehensive support for Indian school education system (Class 1-12)
"""
import uuid
from datetime import datetime, date
from enum import Enum
from sqlalchemy import (
    Column, String, Text, Boolean, DateTime, Integer, 
    Float, JSON, ForeignKey, func, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class EducationBoard(str, Enum):
    """Indian Education Boards"""
    CBSE = "cbse"
    ICSE = "icse"
    MAHARASHTRA = "maharashtra"
    TAMIL_NADU = "tamil_nadu"
    KARNATAKA = "karnataka"
    UTTAR_PRADESH = "uttar_pradesh"
    WEST_BENGAL = "west_bengal"
    RAJASTHAN = "rajasthan"
    GUJARAT = "gujarat"
    ANDHRA_PRADESH = "andhra_pradesh"
    KERALA = "kerala"
    PUNJAB = "punjab"
    HARYANA = "haryana"
    BIHAR = "bihar"
    ODISHA = "odisha"
    ASSAM = "assam"
    JHARKHAND = "jharkhand"
    CHHATTISGARH = "chhattisgarh"
    HIMACHAL_PRADESH = "himachal_pradesh"
    UTTARAKHAND = "uttarakhand"


class ClassLevel(str, Enum):
    """School Class Levels"""
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


class EducationLevel(str, Enum):
    """Education Levels"""
    PRIMARY = "primary"  # Class 1-5
    UPPER_PRIMARY = "upper_primary"  # Class 6-8
    SECONDARY = "secondary"  # Class 9-10
    HIGHER_SECONDARY = "higher_secondary"  # Class 11-12


class Stream(str, Enum):
    """Higher Secondary Streams"""
    SCIENCE = "science"
    COMMERCE = "commerce"
    ARTS = "arts"
    HUMANITIES = "humanities"
    VOCATIONAL = "vocational"


class MediumOfInstruction(str, Enum):
    """Medium of Instruction"""
    ENGLISH = "english"
    HINDI = "hindi"
    MARATHI = "marathi"
    TAMIL = "tamil"
    TELUGU = "telugu"
    KANNADA = "kannada"
    MALAYALAM = "malayalam"
    BENGALI = "bengali"
    GUJARATI = "gujarati"
    PUNJABI = "punjabi"
    URDU = "urdu"
    ASSAMESE = "assamese"
    ODIA = "odia"


class SchoolSubject(Base):
    """School subjects for different classes and boards"""
    __tablename__ = "school_subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Subject identification
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=False)
    display_name = Column(String(150))
    
    # Classification
    education_board = Column(String(50), nullable=False, index=True)
    class_level = Column(String(20), nullable=False, index=True)
    education_level = Column(String(30), nullable=False, index=True)
    
    # Subject details
    is_core_subject = Column(Boolean, default=True)
    is_optional = Column(Boolean, default=False)
    is_language = Column(Boolean, default=False)
    subject_category = Column(String(50))  # Science, Mathematics, Language, Social_Science, etc.
    
    # Stream association (for Class 11-12)
    applicable_streams = Column(JSON)  # List of streams where this subject is available
    
    # Curriculum details
    syllabus_outline = Column(JSON)  # Detailed syllabus structure
    learning_objectives = Column(JSON)  # Learning outcomes
    assessment_pattern = Column(JSON)  # How the subject is assessed
    
    # Prerequisites and progression
    prerequisite_subjects = Column(JSON)  # Required previous subjects
    next_level_subjects = Column(JSON)  # What subjects this leads to
    
    # Practical/Theory components
    has_practical = Column(Boolean, default=False)
    theory_marks = Column(Integer)
    practical_marks = Column(Integer)
    internal_assessment_marks = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    topics = relationship("SchoolTopic", back_populates="subject")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_school_subject_board_class', 'education_board', 'class_level'),
        Index('idx_school_subject_level_category', 'education_level', 'subject_category'),
        Index('idx_school_subject_core_optional', 'is_core_subject', 'is_optional'),
    )
    
    def __repr__(self):
        return f"<SchoolSubject(name={self.name}, board={self.education_board}, class={self.class_level})>"


class SchoolTopic(Base):
    """Topics within school subjects"""
    __tablename__ = "school_topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Topic identification
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False)
    display_name = Column(String(250))
    
    # Hierarchy
    subject_id = Column(UUID(as_uuid=True), ForeignKey("school_subjects.id"), nullable=False)
    parent_topic_id = Column(UUID(as_uuid=True), ForeignKey("school_topics.id"))
    level = Column(Integer, default=0)  # 0=main topic, 1=subtopic, etc.
    sequence_order = Column(Integer, default=0)
    
    # Content details
    description = Column(Text)
    learning_objectives = Column(JSON)
    key_concepts = Column(JSON)
    difficulty_level = Column(String(20), default="intermediate")
    
    # Time allocation
    estimated_hours = Column(Float)
    weightage_percentage = Column(Float)  # Weightage in exams
    
    # Prerequisites
    prerequisite_topics = Column(JSON)  # Required previous topics
    
    # Assessment
    assessment_methods = Column(JSON)  # How this topic is assessed
    sample_questions = Column(JSON)  # Sample question types
    
    # Resources
    reference_materials = Column(JSON)  # Books, videos, etc.
    practical_activities = Column(JSON)  # Hands-on activities
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subject = relationship("SchoolSubject", back_populates="topics")
    parent_topic = relationship("SchoolTopic", remote_side=[id])
    subtopics = relationship("SchoolTopic", back_populates="parent_topic")
    
    # Indexes
    __table_args__ = (
        Index('idx_school_topic_subject_level', 'subject_id', 'level'),
        Index('idx_school_topic_sequence', 'subject_id', 'sequence_order'),
        Index('idx_school_topic_difficulty', 'difficulty_level', 'weightage_percentage'),
    )
    
    def __repr__(self):
        return f"<SchoolTopic(name={self.name}, subject_id={self.subject_id})>"


class SchoolCurriculum(Base):
    """Curriculum structure for different boards and classes"""
    __tablename__ = "school_curricula"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Curriculum identification
    name = Column(String(200), nullable=False)
    code = Column(String(50), nullable=False, unique=True)
    
    # Classification
    education_board = Column(String(50), nullable=False, index=True)
    class_level = Column(String(20), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False, index=True)
    
    # Stream (for Class 11-12)
    stream = Column(String(30))
    
    # Curriculum details
    description = Column(Text)
    objectives = Column(JSON)
    learning_outcomes = Column(JSON)
    
    # Subject structure
    core_subjects = Column(JSON)  # List of mandatory subjects
    optional_subjects = Column(JSON)  # List of optional subjects
    co_curricular_subjects = Column(JSON)  # Art, Music, PE, etc.
    
    # Assessment structure
    assessment_pattern = Column(JSON)  # How students are assessed
    grading_system = Column(JSON)  # Grading scale and criteria
    promotion_criteria = Column(JSON)  # Requirements to move to next class
    
    # Time allocation
    total_teaching_hours = Column(Integer)
    subject_wise_hours = Column(JSON)  # Hours allocated to each subject
    
    # Examination details
    internal_assessment_weightage = Column(Float)
    external_assessment_weightage = Column(Float)
    practical_assessment_weightage = Column(Float)
    
    # Board exam information (for Class 10, 12)
    has_board_exam = Column(Boolean, default=False)
    board_exam_pattern = Column(JSON)
    
    # Status and versioning
    version = Column(String(20), default="1.0")
    is_current = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Approval
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    approver = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_curriculum_board_class_year', 'education_board', 'class_level', 'academic_year'),
        Index('idx_curriculum_stream_current', 'stream', 'is_current'),
        Index('idx_curriculum_board_exam', 'has_board_exam', 'education_board'),
    )
    
    def __repr__(self):
        return f"<SchoolCurriculum(name={self.name}, board={self.education_board}, class={self.class_level})>"


class SchoolAcademicYear(Base):
    """Academic year configuration for schools"""
    __tablename__ = "school_academic_years"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Academic year identification
    year_code = Column(String(20), nullable=False, unique=True, index=True)  # e.g., "2024-25"
    name = Column(String(100), nullable=False)  # e.g., "Academic Year 2024-25"
    
    # Date ranges
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    
    # Term structure
    term_structure = Column(JSON)  # Details about terms/semesters
    
    # Important dates
    admission_start_date = Column(Date)
    admission_end_date = Column(Date)
    exam_schedule = Column(JSON)  # Schedule of various exams
    holiday_calendar = Column(JSON)  # List of holidays
    
    # Status
    is_current = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SchoolAcademicYear(year_code={self.year_code}, is_current={self.is_current})>"


class SchoolGradingSystem(Base):
    """Grading systems for different boards"""
    __tablename__ = "school_grading_systems"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # System identification
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    
    # Board and class applicability
    education_board = Column(String(50), nullable=False, index=True)
    applicable_classes = Column(JSON)  # List of classes where this system applies
    
    # Grading structure
    grading_scale = Column(JSON)  # Grade boundaries and descriptions
    grade_points = Column(JSON)  # Grade point values
    
    # Calculation method
    calculation_method = Column(String(50))  # percentage, cgpa, etc.
    passing_criteria = Column(JSON)  # Minimum requirements to pass
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<SchoolGradingSystem(name={self.name}, board={self.education_board})>"
