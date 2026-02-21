"""
Talent Exam API routes for MEDHASAKTHI
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_admin_user, get_user_institute_context
from app.services.talent_exam_service import talent_exam_service
from app.services.talent_exam_notification_service import talent_exam_notification_service
from app.schemas.talent_exam import (
    TalentExamCreateSchema,
    TalentExamUpdateSchema,
    TalentExamResponseSchema,
    TalentExamRegistrationCreateSchema,
    TalentExamRegistrationUpdateSchema,
    TalentExamRegistrationResponseSchema,
    ExamCenterCreateSchema,
    ExamCenterResponseSchema,
    TalentExamSearchSchema,
    TalentExamSearchResponseSchema,
    TalentExamNotificationCreateSchema,
    TalentExamNotificationResponseSchema,
    TalentExamStatsSchema,
    RegistrationAnalyticsSchema
)
from app.models.talent_exam import (
    TalentExam, TalentExamRegistration, ExamCenter, TalentExamNotification,
    ExamStatus, RegistrationStatus
)
from app.models.user import User

router = APIRouter()


# Super Admin Routes - Talent Exam Management
@router.post("/", response_model=TalentExamResponseSchema)
async def create_talent_exam(
    exam_data: TalentExamCreateSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new talent exam (Super Admin only)"""
    
    success, message, exam = await talent_exam_service.create_talent_exam(
        exam_data.dict(), str(current_user.id), db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return TalentExamResponseSchema.from_orm(exam)


@router.get("/", response_model=TalentExamSearchResponseSchema)
async def search_talent_exams(
    query: Optional[str] = Query(None),
    exam_type: Optional[str] = Query(None),
    class_level: Optional[str] = Query(None),
    academic_year: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search talent exams"""
    
    query_obj = db.query(TalentExam).filter(TalentExam.is_active == True)
    
    # Apply filters
    if query:
        query_obj = query_obj.filter(
            TalentExam.title.ilike(f"%{query}%") |
            TalentExam.exam_code.ilike(f"%{query}%")
        )
    
    if exam_type:
        query_obj = query_obj.filter(TalentExam.exam_type == exam_type)
    
    if class_level:
        query_obj = query_obj.filter(TalentExam.class_level == class_level)
    
    if academic_year:
        query_obj = query_obj.filter(TalentExam.academic_year == academic_year)
    
    if status:
        query_obj = query_obj.filter(TalentExam.status == status)
    
    if date_from:
        query_obj = query_obj.filter(TalentExam.exam_date >= date_from)
    
    if date_to:
        query_obj = query_obj.filter(TalentExam.exam_date <= date_to)
    
    # Get total count
    total = query_obj.count()
    
    # Apply pagination
    exams = query_obj.order_by(TalentExam.exam_date.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    total_pages = (total + limit - 1) // limit
    
    return TalentExamSearchResponseSchema(
        exams=[TalentExamResponseSchema.from_orm(exam) for exam in exams],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@router.get("/{exam_id}", response_model=TalentExamResponseSchema)
async def get_talent_exam(
    exam_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific talent exam"""
    
    exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Talent exam not found"
        )
    
    return TalentExamResponseSchema.from_orm(exam)


@router.put("/{exam_id}", response_model=TalentExamResponseSchema)
async def update_talent_exam(
    exam_id: str,
    exam_data: TalentExamUpdateSchema,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update talent exam (Super Admin only)"""
    
    exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Talent exam not found"
        )
    
    # Update fields
    update_data = exam_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exam, field, value)
    
    exam.updated_at = datetime.now()
    
    db.commit()
    db.refresh(exam)
    
    return TalentExamResponseSchema.from_orm(exam)


@router.post("/{exam_id}/open-registration")
async def open_exam_registration(
    exam_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Open registration for talent exam"""
    
    success, message = await talent_exam_service.open_registration(exam_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"success": True, "message": message}


@router.post("/{exam_id}/close-registration")
async def close_exam_registration(
    exam_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Close registration for talent exam"""
    
    success, message = await talent_exam_service.close_registration(exam_id, db)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {"success": True, "message": message}


@router.get("/{exam_id}/statistics", response_model=dict)
async def get_exam_statistics(
    exam_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive exam statistics"""
    
    stats = await talent_exam_service.get_exam_statistics(exam_id, db)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found"
        )
    
    return stats


# Institute Routes - Registration Management
@router.post("/{exam_id}/register", response_model=TalentExamRegistrationResponseSchema)
async def register_for_exam(
    exam_id: str,
    registration_data: TalentExamRegistrationCreateSchema,
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Register student for talent exam"""
    
    # Verify exam exists and registration is open
    exam = db.query(TalentExam).filter(
        TalentExam.id == exam_id,
        TalentExam.status == ExamStatus.REGISTRATION_OPEN
    ).first()
    
    if not exam:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Exam not found or registration not open"
        )
    
    # Check registration deadline
    if datetime.now() > exam.registration_end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline has passed"
        )
    
    # Check if student already registered
    existing_registration = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.exam_id == exam_id,
        TalentExamRegistration.student_email == registration_data.student_email
    ).first()
    
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student already registered for this exam"
        )
    
    # Generate registration number
    registration_count = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.exam_id == exam_id
    ).count()
    
    registration_number = talent_exam_service.generate_registration_number(
        exam.exam_code, registration_count + 1
    )
    
    # Create registration
    registration = TalentExamRegistration(
        registration_number=registration_number,
        exam_id=exam_id,
        student_id=registration_data.student_id if hasattr(registration_data, 'student_id') else None,
        institute_id=str(user_context["institute"].id),
        student_name=registration_data.student_name,
        student_email=registration_data.student_email,
        student_phone=registration_data.student_phone,
        date_of_birth=registration_data.date_of_birth,
        current_class=registration_data.current_class,
        school_name=registration_data.school_name,
        parent_name=registration_data.parent_name,
        parent_email=registration_data.parent_email,
        parent_phone=registration_data.parent_phone,
        address=registration_data.address,
        special_requirements=registration_data.special_requirements,
        status=RegistrationStatus.PENDING
    )
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    
    return TalentExamRegistrationResponseSchema.from_orm(registration)


@router.get("/{exam_id}/registrations", response_model=List[TalentExamRegistrationResponseSchema])
async def get_exam_registrations(
    exam_id: str,
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Get registrations for an exam (filtered by institute for non-admin users)"""
    
    query = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.exam_id == exam_id
    )
    
    # Filter by institute for non-admin users
    if not current_user.is_superuser:
        institute_id = str(user_context["institute"].id) if user_context["institute"] else None
        if institute_id:
            query = query.filter(TalentExamRegistration.institute_id == institute_id)
    
    if status:
        query = query.filter(TalentExamRegistration.status == status)
    
    registrations = query.order_by(TalentExamRegistration.registration_date.desc()).all()
    
    return [TalentExamRegistrationResponseSchema.from_orm(reg) for reg in registrations]


# Notification Routes
@router.post("/notifications", response_model=TalentExamNotificationResponseSchema)
async def create_notification(
    notification_data: TalentExamNotificationCreateSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create and send talent exam notification"""
    
    success = await talent_exam_notification_service.send_bulk_notification(
        title=notification_data.title,
        message=notification_data.message,
        notification_type=notification_data.notification_type,
        target_class_levels=[level.value for level in notification_data.target_class_levels],
        target_states=notification_data.target_states,
        target_institutes=notification_data.target_institutes,
        send_email=notification_data.send_email,
        send_sms=notification_data.send_sms,
        send_push=notification_data.send_push,
        created_by=str(current_user.id),
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )
    
    # Get the created notification
    notification = db.query(TalentExamNotification).filter(
        TalentExamNotification.created_by == str(current_user.id)
    ).order_by(TalentExamNotification.created_at.desc()).first()
    
    return TalentExamNotificationResponseSchema.from_orm(notification)


@router.get("/notifications", response_model=List[TalentExamNotificationResponseSchema])
async def get_notifications(
    exam_id: Optional[str] = Query(None),
    notification_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get talent exam notifications"""
    
    query = db.query(TalentExamNotification)
    
    if exam_id:
        query = query.filter(TalentExamNotification.exam_id == exam_id)
    
    if notification_type:
        query = query.filter(TalentExamNotification.notification_type == notification_type)
    
    if status:
        query = query.filter(TalentExamNotification.status == status)
    
    notifications = query.order_by(TalentExamNotification.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    return [TalentExamNotificationResponseSchema.from_orm(notif) for notif in notifications]


# Exam Center Routes
@router.post("/centers", response_model=ExamCenterResponseSchema)
async def create_exam_center(
    center_data: ExamCenterCreateSchema,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create exam center"""
    
    # Check if center code already exists
    existing_center = db.query(ExamCenter).filter(
        ExamCenter.center_code == center_data.center_code
    ).first()
    
    if existing_center:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Center code already exists"
        )
    
    center = ExamCenter(**center_data.dict())
    
    db.add(center)
    db.commit()
    db.refresh(center)
    
    return ExamCenterResponseSchema.from_orm(center)


@router.get("/centers", response_model=List[ExamCenterResponseSchema])
async def get_exam_centers(
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get exam centers"""
    
    query = db.query(ExamCenter)
    
    if city:
        query = query.filter(ExamCenter.city.ilike(f"%{city}%"))
    
    if state:
        query = query.filter(ExamCenter.state.ilike(f"%{state}%"))
    
    if is_active is not None:
        query = query.filter(ExamCenter.is_active == is_active)
    
    centers = query.order_by(ExamCenter.center_name).all()
    
    return [ExamCenterResponseSchema.from_orm(center) for center in centers]


# Public Routes
@router.get("/upcoming", response_model=List[TalentExamResponseSchema])
async def get_upcoming_exams(
    class_level: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get upcoming talent exams (public endpoint)"""
    
    upcoming_exams = await talent_exam_service.get_upcoming_exams(class_level, db)
    
    return [TalentExamResponseSchema(**exam) for exam in upcoming_exams[:limit]]


@router.get("/stats/overview", response_model=TalentExamStatsSchema)
async def get_talent_exam_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get talent exam system overview statistics"""
    
    total_exams = db.query(TalentExam).filter(TalentExam.is_active == True).count()
    
    exams_by_status = db.query(
        TalentExam.status,
        db.func.count(TalentExam.id)
    ).filter(TalentExam.is_active == True).group_by(TalentExam.status).all()
    
    exams_by_class = db.query(
        TalentExam.class_level,
        db.func.count(TalentExam.id)
    ).filter(TalentExam.is_active == True).group_by(TalentExam.class_level).all()
    
    exams_by_type = db.query(
        TalentExam.exam_type,
        db.func.count(TalentExam.id)
    ).filter(TalentExam.is_active == True).group_by(TalentExam.exam_type).all()
    
    total_registrations = db.query(TalentExamRegistration).count()
    
    registrations_by_status = db.query(
        TalentExamRegistration.status,
        db.func.count(TalentExamRegistration.id)
    ).group_by(TalentExamRegistration.status).all()
    
    upcoming_exams = await talent_exam_service.get_upcoming_exams(None, db)
    
    return TalentExamStatsSchema(
        total_exams=total_exams,
        exams_by_status=dict(exams_by_status),
        exams_by_class=dict(exams_by_class),
        exams_by_type=dict(exams_by_type),
        total_registrations=total_registrations,
        registrations_by_status=dict(registrations_by_status),
        upcoming_exams=[TalentExamResponseSchema(**exam) for exam in upcoming_exams[:5]],
        recent_results=[]  # TODO: Implement when results system is ready
    )
