"""
Question and exam-related database models
"""
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Float, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum

from app.core.database import Base


class QuestionType(str, Enum):
    """Types of questions"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODE = "code"
    IMAGE_BASED = "image_based"
    AUDIO_BASED = "audio_based"


class DifficultyLevel(str, Enum):
    """Difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionStatus(str, Enum):
    """Question status"""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class Subject(Base):
    """Academic subjects"""
    __tablename__ = "subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), nullable=False, unique=True)
    description = Column(Text)
    
    # Hierarchy
    parent_subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"))
    level = Column(Integer, default=0)  # 0=main subject, 1=sub-subject, etc.
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("Subject", remote_side=[id])
    children = relationship("Subject", back_populates="parent")
    questions = relationship("Question", back_populates="subject")
    
    def __repr__(self):
        return f"<Subject(code={self.code}, name={self.name})>"


class Topic(Base):
    """Topics within subjects"""
    __tablename__ = "topics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Learning objectives
    learning_objectives = Column(JSON)  # Array of learning objectives
    prerequisites = Column(JSON)  # Array of prerequisite topics
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    subject = relationship("Subject")
    questions = relationship("Question", back_populates="topic")
    
    def __repr__(self):
        return f"<Topic(name={self.name}, subject={self.subject_id})>"


class Question(Base):
    """Questions in the question bank"""
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, index=True)
    difficulty_level = Column(String(20), nullable=False, index=True)
    
    # Academic classification
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"))
    grade_level = Column(String(20))
    
    # Question data
    options = Column(JSON)  # For MCQ: [{"id": "A", "text": "Option A", "is_correct": false}]
    correct_answer = Column(Text)  # For non-MCQ questions
    explanation = Column(Text)  # Detailed explanation
    hints = Column(JSON)  # Array of hints
    
    # Media
    image_url = Column(String(500))
    audio_url = Column(String(500))
    video_url = Column(String(500))
    attachments = Column(JSON)  # Array of attachment URLs
    
    # AI Generation metadata
    ai_generated = Column(Boolean, default=False)
    ai_model_used = Column(String(100))  # e.g., "gpt-4", "claude-3"
    generation_prompt = Column(Text)  # Prompt used for generation
    generation_metadata = Column(JSON)  # Additional AI metadata
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)  # 0-100 quality score
    difficulty_score = Column(Float, default=0.0)  # Calculated difficulty
    discrimination_index = Column(Float, default=0.0)  # How well it discriminates
    
    # Usage statistics
    times_used = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)
    average_time_taken = Column(Float, default=0.0)  # In seconds
    
    # Status and approval
    status = Column(String(20), default=QuestionStatus.DRAFT.value, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    approved_at = Column(DateTime(timezone=True))
    
    # Tags and keywords
    tags = Column(ARRAY(String))  # Array of tags
    keywords = Column(ARRAY(String))  # Array of keywords for search
    
    # Relationships
    subject = relationship("Subject", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    approver = relationship("User", foreign_keys=[approved_by])
    
    def __repr__(self):
        return f"<Question(id={self.id}, type={self.question_type}, difficulty={self.difficulty_level})>"


class QuestionBank(Base):
    """Question banks for organizing questions"""
    __tablename__ = "question_banks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Ownership
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Configuration
    is_public = Column(Boolean, default=False)
    is_ai_generated = Column(Boolean, default=False)
    auto_update = Column(Boolean, default=False)  # Auto-update with new AI questions
    
    # Metadata
    total_questions = Column(Integer, default=0)
    subjects_covered = Column(JSON)  # Array of subject IDs
    difficulty_distribution = Column(JSON)  # Distribution of difficulty levels
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    institute = relationship("Institute")
    creator = relationship("User")
    questions = relationship("Question", secondary="question_bank_questions")
    
    def __repr__(self):
        return f"<QuestionBank(name={self.name}, questions={self.total_questions})>"


class QuestionBankQuestion(Base):
    """Many-to-many relationship between question banks and questions"""
    __tablename__ = "question_bank_questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_bank_id = Column(UUID(as_uuid=True), ForeignKey("question_banks.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    
    # Metadata
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    added_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Relationships
    question_bank = relationship("QuestionBank")
    question = relationship("Question")
    added_by_user = relationship("User")


class AIQuestionGeneration(Base):
    """Track AI question generation requests and results"""
    __tablename__ = "ai_question_generations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Request details
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    institute_id = Column(UUID(as_uuid=True), ForeignKey("institutes.id"))
    
    # Generation parameters
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"))
    question_type = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    count_requested = Column(Integer, nullable=False)
    
    # AI configuration
    ai_model = Column(String(100), nullable=False)  # e.g., "gpt-4", "claude-3"
    prompt_template = Column(Text)
    generation_parameters = Column(JSON)  # Temperature, max_tokens, etc.
    
    # Results
    count_generated = Column(Integer, default=0)
    count_approved = Column(Integer, default=0)
    generation_time = Column(Float, default=0.0)  # Time taken in seconds
    cost = Column(Float, default=0.0)  # Cost in USD
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    requester = relationship("User")
    institute = relationship("Institute")
    subject = relationship("Subject")
    topic = relationship("Topic")
    generated_questions = relationship("Question", 
                                     primaryjoin="AIQuestionGeneration.id == foreign(Question.generation_metadata['generation_id'].astext.cast(UUID))",
                                     viewonly=True)
    
    def __repr__(self):
        return f"<AIQuestionGeneration(id={self.id}, status={self.status}, count={self.count_generated})>"


class QuestionFeedback(Base):
    """Feedback on questions for quality improvement"""
    __tablename__ = "question_feedback"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Feedback details
    feedback_type = Column(String(50), nullable=False)  # quality, difficulty, clarity, etc.
    rating = Column(Integer)  # 1-5 rating
    comment = Column(Text)
    
    # Specific issues
    is_unclear = Column(Boolean, default=False)
    is_incorrect = Column(Boolean, default=False)
    is_too_easy = Column(Boolean, default=False)
    is_too_hard = Column(Boolean, default=False)
    has_typos = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    question = relationship("Question")
    user = relationship("User")
    
    def __repr__(self):
        return f"<QuestionFeedback(question_id={self.question_id}, rating={self.rating})>"
