"""
Pydantic schemas for questions and AI generation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from app.models.question import QuestionType, DifficultyLevel, QuestionStatus


class QuestionGenerationRequestSchema(BaseModel):
    """Schema for AI question generation request"""
    subject_id: str
    topic_id: Optional[str] = None
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    count: int = Field(..., ge=1, le=50)  # 1-50 questions per request
    grade_level: Optional[str] = None
    learning_objective: Optional[str] = None
    context: Optional[str] = None
    
    @validator('count')
    def validate_count(cls, v):
        if v < 1 or v > 50:
            raise ValueError('Count must be between 1 and 50')
        return v


class QuestionOptionSchema(BaseModel):
    """Schema for multiple choice options"""
    id: str
    text: str
    is_correct: bool


class QuestionCreateSchema(BaseModel):
    """Schema for creating a question"""
    question_text: str = Field(..., min_length=10, max_length=2000)
    question_type: QuestionType
    difficulty_level: DifficultyLevel
    subject_id: str
    topic_id: Optional[str] = None
    grade_level: Optional[str] = None
    
    # Question data
    options: Optional[List[QuestionOptionSchema]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    
    # Media
    image_url: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    
    # Tags and keywords
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    
    @validator('options')
    def validate_options(cls, v, values):
        question_type = values.get('question_type')
        if question_type == QuestionType.MULTIPLE_CHOICE:
            if not v or len(v) != 4:
                raise ValueError('Multiple choice questions must have exactly 4 options')
            
            correct_count = sum(1 for opt in v if opt.is_correct)
            if correct_count != 1:
                raise ValueError('Multiple choice questions must have exactly one correct answer')
        
        return v


class QuestionUpdateSchema(BaseModel):
    """Schema for updating a question"""
    question_text: Optional[str] = Field(None, min_length=10, max_length=2000)
    difficulty_level: Optional[DifficultyLevel] = None
    grade_level: Optional[str] = None
    options: Optional[List[QuestionOptionSchema]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    keywords: Optional[List[str]] = None
    status: Optional[QuestionStatus] = None


class QuestionResponseSchema(BaseModel):
    """Schema for question response"""
    id: str
    question_text: str
    question_type: str
    difficulty_level: str
    subject_id: str
    topic_id: Optional[str]
    grade_level: Optional[str]
    
    options: Optional[List[Dict[str, Any]]]
    correct_answer: Optional[str]
    explanation: Optional[str]
    hints: Optional[List[str]]
    
    # Media
    image_url: Optional[str]
    audio_url: Optional[str]
    video_url: Optional[str]
    
    # AI metadata
    ai_generated: bool
    ai_model_used: Optional[str]
    
    # Quality metrics
    quality_score: float
    difficulty_score: float
    times_used: int
    times_correct: int
    
    # Status
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Tags and keywords
    tags: Optional[List[str]]
    keywords: Optional[List[str]]
    
    class Config:
        from_attributes = True


class QuestionGenerationResponseSchema(BaseModel):
    """Schema for question generation response"""
    success: bool
    message: str
    generation_id: Optional[str]
    questions_generated: int
    questions: List[QuestionResponseSchema]
    generation_time: float
    cost: Optional[float]


class SubjectCreateSchema(BaseModel):
    """Schema for creating a subject"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    parent_subject_id: Optional[str] = None


class SubjectResponseSchema(BaseModel):
    """Schema for subject response"""
    id: str
    name: str
    code: str
    description: Optional[str]
    parent_subject_id: Optional[str]
    level: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TopicCreateSchema(BaseModel):
    """Schema for creating a topic"""
    subject_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None


class TopicResponseSchema(BaseModel):
    """Schema for topic response"""
    id: str
    subject_id: str
    name: str
    description: Optional[str]
    learning_objectives: Optional[List[str]]
    prerequisites: Optional[List[str]]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionBankCreateSchema(BaseModel):
    """Schema for creating a question bank"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    is_public: bool = False
    is_ai_generated: bool = False
    auto_update: bool = False


class QuestionBankResponseSchema(BaseModel):
    """Schema for question bank response"""
    id: str
    name: str
    description: Optional[str]
    institute_id: Optional[str]
    is_public: bool
    is_ai_generated: bool
    auto_update: bool
    total_questions: int
    subjects_covered: Optional[List[str]]
    difficulty_distribution: Optional[Dict[str, int]]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuestionFeedbackSchema(BaseModel):
    """Schema for question feedback"""
    question_id: str
    feedback_type: str
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    is_unclear: bool = False
    is_incorrect: bool = False
    is_too_easy: bool = False
    is_too_hard: bool = False
    has_typos: bool = False


class QuestionSearchSchema(BaseModel):
    """Schema for question search"""
    query: Optional[str] = None
    subject_id: Optional[str] = None
    topic_id: Optional[str] = None
    question_type: Optional[QuestionType] = None
    difficulty_level: Optional[DifficultyLevel] = None
    grade_level: Optional[str] = None
    tags: Optional[List[str]] = None
    ai_generated: Optional[bool] = None
    status: Optional[QuestionStatus] = None
    
    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


class QuestionSearchResponseSchema(BaseModel):
    """Schema for question search response"""
    questions: List[QuestionResponseSchema]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class AIGenerationStatsSchema(BaseModel):
    """Schema for AI generation statistics"""
    total_generations: int
    total_questions_generated: int
    total_questions_approved: int
    average_generation_time: float
    total_cost: float
    success_rate: float
    
    # Breakdown by type
    by_question_type: Dict[str, int]
    by_difficulty: Dict[str, int]
    by_subject: Dict[str, int]
    
    # Recent activity
    recent_generations: List[Dict[str, Any]]


class BulkQuestionImportSchema(BaseModel):
    """Schema for bulk question import"""
    questions: List[QuestionCreateSchema]
    question_bank_id: Optional[str] = None
    auto_approve: bool = False


class QuestionValidationSchema(BaseModel):
    """Schema for question validation"""
    question_data: Dict[str, Any]
    validation_rules: Optional[Dict[str, Any]] = None


class QuestionValidationResponseSchema(BaseModel):
    """Schema for question validation response"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    quality_score: float
