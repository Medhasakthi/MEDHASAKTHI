"""
Student API routes for MEDHASAKTHI
Student-specific functionality for dashboard, exams, results, and profile management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_student_context
from app.models.user import User, Student, Institute
from app.models.talent_exam import TalentExam, TalentExamRegistration, TalentExamSession
from app.models.certificate import Certificate
from app.models.ai_question import Question, QuestionAttempt
from app.schemas.user import StudentResponseSchema, StudentUpdateSchema
from app.schemas.talent_exam import TalentExamResponseSchema, TalentExamRegistrationResponseSchema
from app.schemas.certificate import CertificateResponseSchema

router = APIRouter()


# Student Dashboard
@router.get("/dashboard")
async def get_student_dashboard(
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get student dashboard data"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any student profile"
        )
    
    # Exam statistics
    total_registrations = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id
    ).count()
    
    completed_exams = db.query(TalentExamSession).filter(
        TalentExamSession.registration_id.in_(
            db.query(TalentExamRegistration.id).filter(
                TalentExamRegistration.student_id == student.id
            )
        ),
        TalentExamSession.is_submitted == True
    ).count()
    
    # Upcoming exams
    upcoming_exams = db.query(TalentExam).join(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id,
        TalentExam.exam_date >= datetime.now().date(),
        TalentExam.status.in_(['registration_open', 'registration_closed', 'ongoing'])
    ).order_by(TalentExam.exam_date).limit(5).all()
    
    # Recent results
    recent_sessions = db.query(TalentExamSession).join(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id,
        TalentExamSession.is_submitted == True,
        TalentExamSession.score.isnot(None)
    ).order_by(TalentExamSession.submission_time.desc()).limit(5).all()
    
    # Certificates earned
    certificates_count = db.query(Certificate).filter(
        Certificate.recipient_email == student.email
    ).count()
    
    # Study statistics
    questions_attempted = db.query(QuestionAttempt).filter(
        QuestionAttempt.student_id == student.id
    ).count()
    
    correct_answers = db.query(QuestionAttempt).filter(
        QuestionAttempt.student_id == student.id,
        QuestionAttempt.is_correct == True
    ).count()
    
    accuracy = (correct_answers / questions_attempted * 100) if questions_attempted > 0 else 0
    
    # Performance trends (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_performance = db.query(
        func.date(QuestionAttempt.attempted_at).label('date'),
        func.count(QuestionAttempt.id).label('attempts'),
        func.avg(func.cast(QuestionAttempt.is_correct, db.Integer)).label('accuracy')
    ).filter(
        QuestionAttempt.student_id == student.id,
        QuestionAttempt.attempted_at >= thirty_days_ago
    ).group_by(func.date(QuestionAttempt.attempted_at)).all()
    
    return {
        "student_info": {
            "name": student.full_name,
            "student_id": student.student_id,
            "class": student.current_class,
            "institute": student.institute.name if student.institute else None
        },
        "exam_statistics": {
            "total_registrations": total_registrations,
            "completed_exams": completed_exams,
            "upcoming_exams": len(upcoming_exams),
            "certificates_earned": certificates_count
        },
        "study_statistics": {
            "questions_attempted": questions_attempted,
            "correct_answers": correct_answers,
            "accuracy_percentage": round(accuracy, 2)
        },
        "upcoming_exams": [
            {
                "id": exam.id,
                "title": exam.title,
                "exam_date": exam.exam_date.isoformat(),
                "exam_time": exam.exam_time.isoformat(),
                "status": exam.status
            }
            for exam in upcoming_exams
        ],
        "recent_results": [
            {
                "exam_title": session.registration.exam.title if session.registration else "Unknown",
                "score": session.score,
                "percentage": session.percentage,
                "submission_date": session.submission_time.isoformat() if session.submission_time else None
            }
            for session in recent_sessions
        ],
        "performance_trends": [
            {
                "date": date.isoformat(),
                "attempts": attempts,
                "accuracy": round(float(accuracy or 0), 2)
            }
            for date, attempts, accuracy in daily_performance
        ]
    }


# Student Profile
@router.get("/profile", response_model=StudentResponseSchema)
async def get_student_profile(
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get student profile"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return student


@router.put("/profile", response_model=StudentResponseSchema)
async def update_student_profile(
    profile_data: StudentUpdateSchema,
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Update student profile"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    # Update fields
    update_data = profile_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    student.updated_at = datetime.now()
    
    db.commit()
    db.refresh(student)
    
    return student


# Exam Management
@router.get("/exams/available", response_model=List[TalentExamResponseSchema])
async def get_available_exams(
    class_level: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get available exams for the student"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    query = db.query(TalentExam).filter(
        TalentExam.is_active == True,
        TalentExam.status.in_(['scheduled', 'registration_open']),
        TalentExam.exam_date >= datetime.now().date()
    )
    
    # Filter by student's class if not specified
    if not class_level:
        class_level = student.current_class
    
    if class_level:
        query = query.filter(TalentExam.class_level == class_level)
    
    if exam_type:
        query = query.filter(TalentExam.exam_type == exam_type)
    
    exams = query.order_by(TalentExam.exam_date).all()
    
    return exams


@router.get("/exams/registered", response_model=List[TalentExamRegistrationResponseSchema])
async def get_registered_exams(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get exams the student is registered for"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    query = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id
    )
    
    if status:
        query = query.filter(TalentExamRegistration.status == status)
    
    registrations = query.order_by(TalentExamRegistration.registration_date.desc()).all()
    
    return registrations


@router.get("/exams/{exam_id}/session")
async def get_exam_session(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get or create exam session for the student"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    # Check if student is registered for this exam
    registration = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.exam_id == exam_id,
        TalentExamRegistration.student_id == student.id,
        TalentExamRegistration.status == 'confirmed'
    ).first()
    
    if not registration:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student not registered for this exam"
        )
    
    # Check if exam is ongoing
    exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
    if exam.status != 'ongoing':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exam is not currently ongoing"
        )
    
    # Get or create session
    session = db.query(TalentExamSession).filter(
        TalentExamSession.exam_id == exam_id,
        TalentExamSession.registration_id == registration.id
    ).first()
    
    if not session:
        # Create new session
        session = TalentExamSession(
            exam_id=exam_id,
            registration_id=registration.id,
            session_token=f"session_{datetime.now().timestamp()}",
            status="not_started"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    return {
        "session_id": session.id,
        "session_token": session.session_token,
        "exam_title": exam.title,
        "duration_minutes": exam.duration_minutes,
        "total_questions": exam.total_questions,
        "status": session.status,
        "started_at": session.started_at.isoformat() if session.started_at else None,
        "time_remaining": None  # Calculate based on duration and start time
    }


# Results and Performance
@router.get("/results")
async def get_student_results(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get student exam results"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    # Get completed exam sessions
    query = db.query(TalentExamSession).join(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id,
        TalentExamSession.is_submitted == True,
        TalentExamSession.score.isnot(None)
    )
    
    total = query.count()
    
    sessions = query.order_by(TalentExamSession.submission_time.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    results = []
    for session in sessions:
        exam = session.exam
        registration = session.registration
        
        results.append({
            "exam_id": exam.id,
            "exam_title": exam.title,
            "exam_code": exam.exam_code,
            "exam_date": exam.exam_date.isoformat(),
            "score": session.score,
            "percentage": session.percentage,
            "rank": session.rank,
            "total_marks": exam.total_marks,
            "submission_time": session.submission_time.isoformat() if session.submission_time else None,
            "duration_taken": session.duration_seconds,
            "questions_attempted": session.questions_attempted,
            "questions_answered": session.questions_answered
        })
    
    return {
        "results": results,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit
    }


@router.get("/results/{exam_id}/detailed")
async def get_detailed_result(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get detailed result for a specific exam"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    # Get exam session
    session = db.query(TalentExamSession).join(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id,
        TalentExamSession.exam_id == exam_id,
        TalentExamSession.is_submitted == True
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam result not found"
        )
    
    exam = session.exam
    
    # Calculate subject-wise performance
    responses = session.responses or {}
    subject_performance = {}
    
    # This would require question-subject mapping
    # For now, return basic information
    
    return {
        "exam_info": {
            "title": exam.title,
            "exam_code": exam.exam_code,
            "exam_date": exam.exam_date.isoformat(),
            "total_marks": exam.total_marks,
            "passing_marks": exam.passing_marks
        },
        "performance": {
            "score": session.score,
            "percentage": session.percentage,
            "rank": session.rank,
            "questions_attempted": session.questions_attempted,
            "questions_answered": session.questions_answered,
            "duration_taken": session.duration_seconds
        },
        "subject_wise_performance": subject_performance,
        "responses": responses if session.score else None  # Only show if exam is completed
    }


# Certificates
@router.get("/certificates", response_model=List[CertificateResponseSchema])
async def get_student_certificates(
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get certificates earned by the student"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    certificates = db.query(Certificate).filter(
        Certificate.recipient_email == student.email
    ).order_by(Certificate.issued_at.desc()).all()
    
    return certificates


# Study Materials and Practice
@router.get("/practice/questions")
async def get_practice_questions(
    subject: Optional[str] = Query(None),
    difficulty: Optional[str] = Query(None),
    question_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Get practice questions for the student"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    query = db.query(Question).filter(Question.is_active == True)
    
    if subject:
        query = query.filter(Question.subject == subject)
    
    if difficulty:
        query = query.filter(Question.difficulty_level == difficulty)
    
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    # Get questions not recently attempted by the student
    recent_attempts = db.query(QuestionAttempt.question_id).filter(
        QuestionAttempt.student_id == student.id,
        QuestionAttempt.attempted_at >= datetime.now() - timedelta(days=7)
    ).subquery()
    
    query = query.filter(~Question.id.in_(recent_attempts))
    
    questions = query.order_by(func.random()).limit(limit).all()
    
    return [
        {
            "id": q.id,
            "question_text": q.question_text,
            "options": q.options,
            "question_type": q.question_type,
            "subject": q.subject,
            "difficulty_level": q.difficulty_level,
            "marks": q.marks
        }
        for q in questions
    ]


@router.post("/practice/submit")
async def submit_practice_answer(
    question_id: str,
    answer: str,
    time_taken: int,  # in seconds
    current_user: User = Depends(get_current_user),
    student_context: dict = Depends(get_student_context),
    db: Session = Depends(get_db)
):
    """Submit answer for practice question"""
    
    student = student_context["student"]
    if not student:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student profile not found"
        )
    
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if answer is correct
    is_correct = answer.lower().strip() == question.correct_answer.lower().strip()
    
    # Record attempt
    attempt = QuestionAttempt(
        question_id=question_id,
        student_id=student.id,
        answer_given=answer,
        is_correct=is_correct,
        time_taken_seconds=time_taken,
        attempted_at=datetime.now()
    )
    
    db.add(attempt)
    db.commit()
    
    return {
        "is_correct": is_correct,
        "correct_answer": question.correct_answer if not is_correct else None,
        "explanation": question.explanation,
        "marks_earned": question.marks if is_correct else 0
    }
