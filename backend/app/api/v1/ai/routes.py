"""
AI services API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import time

from app.core.database import get_db
from app.services.ai_question_service import ai_question_generator
from app.schemas.question import (
    QuestionGenerationRequestSchema,
    QuestionGenerationResponseSchema,
    QuestionResponseSchema,
    SubjectCreateSchema,
    SubjectResponseSchema,
    TopicCreateSchema,
    TopicResponseSchema,
    QuestionSearchSchema,
    QuestionSearchResponseSchema,
    AIGenerationStatsSchema,
    QuestionValidationSchema,
    QuestionValidationResponseSchema
)
from app.models.question import (
    Subject, Topic, Question, AIQuestionGeneration,
    QuestionType, DifficultyLevel, QuestionStatus
)
from app.models.user import User
from app.api.v1.auth.dependencies import (
    get_current_verified_user,
    get_teacher_user,
    get_institute_admin_user,
    get_super_admin_user,
    get_user_institute_context
)

router = APIRouter()


@router.post("/generate-questions", response_model=QuestionGenerationResponseSchema)
async def generate_questions(
    request: QuestionGenerationRequestSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_teacher_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Generate questions using AI"""
    try:
        start_time = time.time()
        
        # Validate subject exists
        subject = db.query(Subject).filter(Subject.id == request.subject_id).first()
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        # Validate topic if provided
        if request.topic_id:
            topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
            if not topic:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Topic not found"
                )
        
        # Generate questions
        success, message, questions_data = await ai_question_generator.generate_questions(
            subject_id=request.subject_id,
            topic_id=request.topic_id,
            question_type=request.question_type,
            difficulty_level=request.difficulty_level,
            count=request.count,
            grade_level=request.grade_level,
            learning_objective=request.learning_objective,
            context=request.context,
            user_id=str(current_user.id),
            institute_id=str(user_context["institute"].id) if user_context["institute"] else None,
            db=db
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Save questions to database in background
        if questions_data:
            background_tasks.add_task(
                save_questions_background,
                questions_data,
                str(current_user.id),
                db
            )
        
        generation_time = time.time() - start_time
        
        # Convert to response format
        question_responses = []
        for q_data in questions_data:
            question_responses.append(QuestionResponseSchema(
                id=q_data.get("id", "pending"),
                question_text=q_data["question_text"],
                question_type=q_data["question_type"],
                difficulty_level=q_data["difficulty_level"],
                subject_id=q_data["subject_id"],
                topic_id=q_data.get("topic_id"),
                grade_level=q_data.get("grade_level"),
                options=q_data.get("options"),
                correct_answer=q_data.get("correct_answer"),
                explanation=q_data.get("explanation"),
                hints=q_data.get("hints"),
                image_url=q_data.get("image_url"),
                audio_url=q_data.get("audio_url"),
                video_url=q_data.get("video_url"),
                ai_generated=q_data.get("ai_generated", True),
                ai_model_used=q_data.get("ai_model_used"),
                quality_score=0.0,
                difficulty_score=0.0,
                times_used=0,
                times_correct=0,
                status=q_data.get("status", QuestionStatus.PENDING_REVIEW.value),
                created_at=datetime.utcnow(),
                updated_at=None,
                tags=q_data.get("tags", []),
                keywords=q_data.get("keywords", [])
            ))
        
        return QuestionGenerationResponseSchema(
            success=True,
            message=message,
            generation_id=None,  # Will be set when saved
            questions_generated=len(questions_data),
            questions=question_responses,
            generation_time=generation_time,
            cost=0.0  # Calculate based on AI service used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question generation failed: {str(e)}"
        )


async def save_questions_background(questions_data: List[Dict[str, Any]], created_by: str, db: Session):
    """Background task to save generated questions"""
    try:
        success, message, question_ids = await ai_question_generator.save_generated_questions(
            questions_data, created_by, db
        )
        print(f"Background save result: {message}")
    except Exception as e:
        print(f"Background save error: {str(e)}")


@router.get("/subjects", response_model=List[SubjectResponseSchema])
async def get_subjects(
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get all subjects"""
    subjects = db.query(Subject).filter(Subject.is_active == True).all()
    return [SubjectResponseSchema.from_orm(subject) for subject in subjects]


@router.post("/subjects", response_model=SubjectResponseSchema)
async def create_subject(
    subject_data: SubjectCreateSchema,
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new subject"""
    # Check if subject code already exists
    existing = db.query(Subject).filter(Subject.code == subject_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subject code already exists"
        )
    
    # Validate parent subject if provided
    if subject_data.parent_subject_id:
        parent = db.query(Subject).filter(Subject.id == subject_data.parent_subject_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent subject not found"
            )
    
    subject = Subject(
        name=subject_data.name,
        code=subject_data.code,
        description=subject_data.description,
        parent_subject_id=subject_data.parent_subject_id,
        level=1 if subject_data.parent_subject_id else 0
    )
    
    db.add(subject)
    db.commit()
    db.refresh(subject)
    
    return SubjectResponseSchema.from_orm(subject)


@router.get("/subjects/{subject_id}/topics", response_model=List[TopicResponseSchema])
async def get_subject_topics(
    subject_id: str,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Get topics for a subject"""
    # Validate subject exists
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    topics = db.query(Topic).filter(
        Topic.subject_id == subject_id,
        Topic.is_active == True
    ).all()
    
    return [TopicResponseSchema.from_orm(topic) for topic in topics]


@router.post("/topics", response_model=TopicResponseSchema)
async def create_topic(
    topic_data: TopicCreateSchema,
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Create a new topic"""
    # Validate subject exists
    subject = db.query(Subject).filter(Subject.id == topic_data.subject_id).first()
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    topic = Topic(
        subject_id=topic_data.subject_id,
        name=topic_data.name,
        description=topic_data.description,
        learning_objectives=topic_data.learning_objectives,
        prerequisites=topic_data.prerequisites
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    return TopicResponseSchema.from_orm(topic)


@router.post("/questions/search", response_model=QuestionSearchResponseSchema)
async def search_questions(
    search_params: QuestionSearchSchema,
    current_user: User = Depends(get_current_verified_user),
    db: Session = Depends(get_db)
):
    """Search questions with filters"""
    query = db.query(Question)
    
    # Apply filters
    if search_params.query:
        query = query.filter(Question.question_text.ilike(f"%{search_params.query}%"))
    
    if search_params.subject_id:
        query = query.filter(Question.subject_id == search_params.subject_id)
    
    if search_params.topic_id:
        query = query.filter(Question.topic_id == search_params.topic_id)
    
    if search_params.question_type:
        query = query.filter(Question.question_type == search_params.question_type.value)
    
    if search_params.difficulty_level:
        query = query.filter(Question.difficulty_level == search_params.difficulty_level.value)
    
    if search_params.grade_level:
        query = query.filter(Question.grade_level == search_params.grade_level)
    
    if search_params.ai_generated is not None:
        query = query.filter(Question.ai_generated == search_params.ai_generated)
    
    if search_params.status:
        query = query.filter(Question.status == search_params.status.value)
    
    # Apply sorting
    if search_params.sort_by == "created_at":
        if search_params.sort_order == "desc":
            query = query.order_by(Question.created_at.desc())
        else:
            query = query.order_by(Question.created_at.asc())
    elif search_params.sort_by == "quality_score":
        if search_params.sort_order == "desc":
            query = query.order_by(Question.quality_score.desc())
        else:
            query = query.order_by(Question.quality_score.asc())
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (search_params.page - 1) * search_params.page_size
    questions = query.offset(offset).limit(search_params.page_size).all()
    
    # Calculate pagination info
    total_pages = (total + search_params.page_size - 1) // search_params.page_size
    has_next = search_params.page < total_pages
    has_prev = search_params.page > 1
    
    return QuestionSearchResponseSchema(
        questions=[QuestionResponseSchema.from_orm(q) for q in questions],
        total=total,
        page=search_params.page,
        page_size=search_params.page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


@router.get("/generation-stats", response_model=AIGenerationStatsSchema)
async def get_generation_stats(
    current_user: User = Depends(get_institute_admin_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Get AI generation statistics"""
    # Base query for user's institute
    base_query = db.query(AIQuestionGeneration)
    if user_context["institute"]:
        base_query = base_query.filter(
            AIQuestionGeneration.institute_id == user_context["institute"].id
        )
    
    # Calculate statistics
    total_generations = base_query.count()
    completed_generations = base_query.filter(
        AIQuestionGeneration.status == "completed"
    ).all()
    
    total_questions_generated = sum(g.count_generated for g in completed_generations)
    total_questions_approved = sum(g.count_approved for g in completed_generations)
    total_cost = sum(g.cost for g in completed_generations)
    
    if completed_generations:
        average_generation_time = sum(g.generation_time for g in completed_generations) / len(completed_generations)
        success_rate = len(completed_generations) / total_generations * 100
    else:
        average_generation_time = 0.0
        success_rate = 0.0
    
    # Get breakdowns (simplified for now)
    by_question_type = {}
    by_difficulty = {}
    by_subject = {}
    
    for generation in completed_generations:
        # Question type breakdown
        q_type = generation.question_type
        by_question_type[q_type] = by_question_type.get(q_type, 0) + generation.count_generated
        
        # Difficulty breakdown
        difficulty = generation.difficulty_level
        by_difficulty[difficulty] = by_difficulty.get(difficulty, 0) + generation.count_generated
    
    # Recent generations
    recent = base_query.order_by(AIQuestionGeneration.created_at.desc()).limit(10).all()
    recent_generations = [
        {
            "id": str(g.id),
            "created_at": g.created_at.isoformat(),
            "question_type": g.question_type,
            "difficulty_level": g.difficulty_level,
            "count_generated": g.count_generated,
            "status": g.status
        }
        for g in recent
    ]
    
    return AIGenerationStatsSchema(
        total_generations=total_generations,
        total_questions_generated=total_questions_generated,
        total_questions_approved=total_questions_approved,
        average_generation_time=average_generation_time,
        total_cost=total_cost,
        success_rate=success_rate,
        by_question_type=by_question_type,
        by_difficulty=by_difficulty,
        by_subject=by_subject,
        recent_generations=recent_generations
    )


@router.post("/validate-question", response_model=QuestionValidationResponseSchema)
async def validate_question(
    validation_request: QuestionValidationSchema,
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Validate a question using AI"""
    # This is a placeholder for question validation logic
    # In a full implementation, you would use AI to validate:
    # - Grammar and spelling
    # - Question clarity
    # - Answer correctness
    # - Difficulty appropriateness
    
    question_data = validation_request.question_data
    errors = []
    warnings = []
    suggestions = []
    
    # Basic validation
    if not question_data.get("question_text"):
        errors.append("Question text is required")
    
    if len(question_data.get("question_text", "")) < 10:
        warnings.append("Question text seems too short")
    
    if question_data.get("question_type") == "multiple_choice":
        options = question_data.get("options", [])
        if len(options) != 4:
            errors.append("Multiple choice questions must have exactly 4 options")
        
        correct_count = sum(1 for opt in options if opt.get("is_correct", False))
        if correct_count != 1:
            errors.append("Multiple choice questions must have exactly one correct answer")
    
    # Calculate quality score (simplified)
    quality_score = 100.0
    if errors:
        quality_score -= len(errors) * 20
    if warnings:
        quality_score -= len(warnings) * 10
    
    quality_score = max(0.0, quality_score)
    
    return QuestionValidationResponseSchema(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions,
        quality_score=quality_score
    )


# Import datetime for response schemas
from datetime import datetime
