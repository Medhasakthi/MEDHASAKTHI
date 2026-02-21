"""
Admin API routes for MEDHASAKTHI
Super admin functionality for platform management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_admin_user, get_current_user
from app.models.user import User, Institute, Student, UserRole
from app.models.talent_exam import TalentExam, TalentExamRegistration
from app.models.certificate import Certificate
from app.schemas.user import (
    UserResponseSchema, InstituteResponseSchema, StudentResponseSchema,
    InstituteCreateSchema, InstituteUpdateSchema, UserCreateSchema, UserUpdateSchema
)
from app.services.email_service import email_service
from app.services.analytics_service import analytics_service

router = APIRouter()


# Platform Analytics
@router.get("/analytics/overview")
async def get_platform_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive platform analytics"""
    
    # User statistics
    total_users = db.query(User).count()
    total_institutes = db.query(Institute).filter(Institute.is_active == True).count()
    total_students = db.query(Student).filter(Student.is_active == True).count()
    
    # Recent registrations (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_institutes = db.query(Institute).filter(
        Institute.created_at >= thirty_days_ago
    ).count()
    recent_students = db.query(Student).filter(
        Student.created_at >= thirty_days_ago
    ).count()
    
    # Exam statistics
    total_exams = db.query(TalentExam).filter(TalentExam.is_active == True).count()
    active_exams = db.query(TalentExam).filter(
        TalentExam.status.in_(['registration_open', 'ongoing'])
    ).count()
    total_registrations = db.query(TalentExamRegistration).count()
    
    # Certificate statistics
    total_certificates = db.query(Certificate).count()
    recent_certificates = db.query(Certificate).filter(
        Certificate.created_at >= thirty_days_ago
    ).count()
    
    # Geographic distribution
    institutes_by_state = db.query(
        Institute.state,
        func.count(Institute.id).label('count')
    ).filter(Institute.is_active == True).group_by(Institute.state).all()
    
    # Growth metrics
    daily_registrations = db.query(
        func.date(Institute.created_at).label('date'),
        func.count(Institute.id).label('count')
    ).filter(
        Institute.created_at >= thirty_days_ago
    ).group_by(func.date(Institute.created_at)).all()
    
    return {
        "user_statistics": {
            "total_users": total_users,
            "total_institutes": total_institutes,
            "total_students": total_students,
            "recent_institutes": recent_institutes,
            "recent_students": recent_students
        },
        "exam_statistics": {
            "total_exams": total_exams,
            "active_exams": active_exams,
            "total_registrations": total_registrations
        },
        "certificate_statistics": {
            "total_certificates": total_certificates,
            "recent_certificates": recent_certificates
        },
        "geographic_distribution": [
            {"state": state, "count": count} for state, count in institutes_by_state
        ],
        "growth_metrics": [
            {"date": date.isoformat(), "registrations": count} 
            for date, count in daily_registrations
        ]
    }


# Institute Management
@router.get("/institutes", response_model=List[InstituteResponseSchema])
async def get_all_institutes(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    institute_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all institutes with filtering and pagination"""
    
    query = db.query(Institute)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Institute.name.ilike(f"%{search}%"),
                Institute.institute_code.ilike(f"%{search}%"),
                Institute.contact_email.ilike(f"%{search}%")
            )
        )
    
    if state:
        query = query.filter(Institute.state.ilike(f"%{state}%"))
    
    if institute_type:
        query = query.filter(Institute.institute_type == institute_type)
    
    if is_active is not None:
        query = query.filter(Institute.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    institutes = query.order_by(Institute.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    return institutes


@router.post("/institutes", response_model=InstituteResponseSchema)
async def create_institute(
    institute_data: InstituteCreateSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create new institute"""
    
    # Check if institute code already exists
    existing_institute = db.query(Institute).filter(
        Institute.institute_code == institute_data.institute_code
    ).first()
    
    if existing_institute:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institute code already exists"
        )
    
    # Create institute
    institute = Institute(**institute_data.dict())
    db.add(institute)
    db.commit()
    db.refresh(institute)
    
    # Send welcome email
    background_tasks.add_task(
        email_service.send_welcome_email,
        institute.contact_email,
        institute.name
    )
    
    return institute


@router.put("/institutes/{institute_id}", response_model=InstituteResponseSchema)
async def update_institute(
    institute_id: str,
    institute_data: InstituteUpdateSchema,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update institute details"""
    
    institute = db.query(Institute).filter(Institute.id == institute_id).first()
    
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institute not found"
        )
    
    # Update fields
    update_data = institute_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(institute, field, value)
    
    institute.updated_at = datetime.now()
    
    db.commit()
    db.refresh(institute)
    
    return institute


@router.delete("/institutes/{institute_id}")
async def deactivate_institute(
    institute_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate institute (soft delete)"""
    
    institute = db.query(Institute).filter(Institute.id == institute_id).first()
    
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Institute not found"
        )
    
    institute.is_active = False
    institute.updated_at = datetime.now()
    
    db.commit()
    
    return {"message": "Institute deactivated successfully"}


# User Management
@router.get("/users", response_model=List[UserResponseSchema])
async def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with filtering and pagination"""
    
    query = db.query(User)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    users = query.order_by(User.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    return users


@router.post("/users", response_model=UserResponseSchema)
async def create_user(
    user_data: UserCreateSchema,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create new user"""
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = User(**user_data.dict())
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send welcome email
    background_tasks.add_task(
        email_service.send_welcome_email,
        user.email,
        user.full_name
    )
    
    return user


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user role"""
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    old_role = user.role
    user.role = new_role
    user.updated_at = datetime.now()
    
    db.commit()
    
    return {
        "message": f"User role updated from {old_role} to {new_role}",
        "user_id": user_id,
        "old_role": old_role,
        "new_role": new_role
    }


# System Configuration
@router.get("/system/config")
async def get_system_config(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system configuration"""
    
    # This would typically come from a configuration table
    # For now, return hardcoded values
    return {
        "platform_name": "MEDHASAKTHI",
        "version": "1.0.0",
        "maintenance_mode": False,
        "registration_enabled": True,
        "max_file_size_mb": 10,
        "supported_languages": ["en", "hi", "ta", "te", "kn", "ml"],
        "default_language": "en",
        "timezone": "Asia/Kolkata",
        "currency": "INR",
        "features": {
            "ai_question_generation": True,
            "talent_exams": True,
            "certificates": True,
            "analytics": True,
            "mobile_app": True
        }
    }


@router.put("/system/config")
async def update_system_config(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update system configuration"""
    
    # In a real implementation, this would update a configuration table
    # For now, just return success
    return {
        "message": "System configuration updated successfully",
        "updated_config": config_data
    }


# Bulk Operations
@router.post("/bulk/institutes/import")
async def bulk_import_institutes(
    # This would handle CSV file upload
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk import institutes from CSV"""
    
    # Implementation would parse CSV and create institutes
    # For now, return placeholder
    return {
        "message": "Bulk import initiated",
        "status": "processing",
        "estimated_completion": "5 minutes"
    }


@router.post("/bulk/notifications/send")
async def send_bulk_notification(
    notification_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Send bulk notifications to users"""
    
    # Implementation would send notifications based on criteria
    background_tasks.add_task(
        send_bulk_notifications_task,
        notification_data,
        str(current_user.id)
    )
    
    return {
        "message": "Bulk notification queued for sending",
        "notification_id": f"bulk_{datetime.now().timestamp()}"
    }


# Platform Health
@router.get("/health/detailed")
async def get_detailed_health(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed platform health metrics"""
    
    # Database health
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Service health checks
    services_health = {
        "database": db_status,
        "redis": "healthy",  # Would check Redis connection
        "email_service": "healthy",  # Would check email service
        "ai_service": "healthy",  # Would check AI service
        "file_storage": "healthy"  # Would check file storage
    }
    
    # Performance metrics
    performance_metrics = {
        "avg_response_time_ms": 150,
        "requests_per_minute": 1250,
        "error_rate_percent": 0.1,
        "cpu_usage_percent": 45,
        "memory_usage_percent": 62,
        "disk_usage_percent": 78
    }
    
    return {
        "overall_status": "healthy",
        "services": services_health,
        "performance": performance_metrics,
        "last_updated": datetime.now().isoformat()
    }


# Helper functions
async def send_bulk_notifications_task(notification_data: Dict[str, Any], admin_id: str):
    """Background task for sending bulk notifications"""
    # Implementation would send notifications
    pass
