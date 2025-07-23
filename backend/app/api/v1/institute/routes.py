"""
Institute API routes for MEDHASAKTHI
Institute-specific functionality for managing students, teachers, and courses
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_user_institute_context
from app.models.user import User, Institute, Student, Teacher
from app.models.talent_exam import TalentExam, TalentExamRegistration
from app.models.certificate import Certificate
from app.schemas.user import (
    StudentResponseSchema, StudentCreateSchema, StudentUpdateSchema,
    TeacherResponseSchema, TeacherCreateSchema, TeacherUpdateSchema
)
from app.services.file_service import file_service
from app.services.email_service import email_service

router = APIRouter()

# Include bulk student management routes
from app.api.v1.institute.student_bulk_routes import router as student_bulk_router
router.include_router(student_bulk_router, prefix="/students/bulk", tags=["Student Bulk Management"])

# Include bulk teacher management routes
from app.api.v1.institute.teacher_bulk_routes import router as teacher_bulk_router
router.include_router(teacher_bulk_router, prefix="/teachers/bulk", tags=["Teacher Bulk Management"])


# Institute Dashboard
@router.get("/dashboard")
async def get_institute_dashboard(
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Get institute dashboard data"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    # Student statistics
    total_students = db.query(Student).filter(
        Student.institute_id == institute.id,
        Student.is_active == True
    ).count()
    
    recent_students = db.query(Student).filter(
        Student.institute_id == institute.id,
        Student.created_at >= datetime.now() - timedelta(days=30)
    ).count()
    
    # Teacher statistics
    total_teachers = db.query(Teacher).filter(
        Teacher.institute_id == institute.id,
        Teacher.is_active == True
    ).count()
    
    # Exam registrations
    exam_registrations = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.institute_id == institute.id
    ).count()
    
    recent_registrations = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.institute_id == institute.id,
        TalentExamRegistration.registration_date >= datetime.now() - timedelta(days=30)
    ).count()
    
    # Certificates issued
    certificates_issued = db.query(Certificate).join(Student).filter(
        Student.institute_id == institute.id
    ).count()
    
    # Class-wise distribution
    class_distribution = db.query(
        Student.current_class,
        func.count(Student.id).label('count')
    ).filter(
        Student.institute_id == institute.id,
        Student.is_active == True
    ).group_by(Student.current_class).all()
    
    # Recent activities
    recent_activities = []
    
    # Recent student registrations
    recent_student_regs = db.query(Student).filter(
        Student.institute_id == institute.id,
        Student.created_at >= datetime.now() - timedelta(days=7)
    ).order_by(Student.created_at.desc()).limit(5).all()
    
    for student in recent_student_regs:
        recent_activities.append({
            "type": "student_registration",
            "description": f"New student {student.full_name} registered",
            "timestamp": student.created_at.isoformat()
        })
    
    return {
        "institute_info": {
            "name": institute.name,
            "code": institute.institute_code,
            "type": institute.institute_type,
            "city": institute.city,
            "state": institute.state
        },
        "statistics": {
            "total_students": total_students,
            "recent_students": recent_students,
            "total_teachers": total_teachers,
            "exam_registrations": exam_registrations,
            "recent_registrations": recent_registrations,
            "certificates_issued": certificates_issued
        },
        "class_distribution": [
            {"class": cls, "count": count} for cls, count in class_distribution
        ],
        "recent_activities": recent_activities
    }


# Student Management
@router.get("/students", response_model=List[StudentResponseSchema])
async def get_institute_students(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    class_level: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Get students belonging to the institute"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    query = db.query(Student).filter(Student.institute_id == institute.id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Student.full_name.ilike(f"%{search}%"),
                Student.email.ilike(f"%{search}%"),
                Student.student_id.ilike(f"%{search}%")
            )
        )
    
    if class_level:
        query = query.filter(Student.current_class == class_level)
    
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    students = query.order_by(Student.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    return students


@router.post("/students", response_model=StudentResponseSchema)
async def create_student(
    student_data: StudentCreateSchema,
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Create new student in the institute"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    # Check if student ID already exists in the institute
    existing_student = db.query(Student).filter(
        Student.institute_id == institute.id,
        Student.student_id == student_data.student_id
    ).first()
    
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID already exists in this institute"
        )
    
    # Create student
    student = Student(
        **student_data.dict(),
        institute_id=institute.id,
        created_by=current_user.id
    )
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return student


@router.put("/students/{student_id}", response_model=StudentResponseSchema)
async def update_student(
    student_id: str,
    student_data: StudentUpdateSchema,
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Update student details"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    student = db.query(Student).filter(
        Student.id == student_id,
        Student.institute_id == institute.id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Update fields
    update_data = student_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(student, field, value)
    
    student.updated_at = datetime.now()
    
    db.commit()
    db.refresh(student)
    
    return student


@router.post("/students/bulk-import")
async def bulk_import_students(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Bulk import students from CSV file"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )
    
    try:
        # Read and process CSV file
        content = await file.read()
        csv_data = content.decode('utf-8')
        
        # Process CSV and create students
        # This is a simplified implementation
        lines = csv_data.strip().split('\n')
        headers = lines[0].split(',')
        
        created_students = []
        errors = []
        
        for i, line in enumerate(lines[1:], 1):
            try:
                values = line.split(',')
                student_data = dict(zip(headers, values))
                
                # Create student
                student = Student(
                    full_name=student_data.get('full_name', '').strip(),
                    email=student_data.get('email', '').strip(),
                    student_id=student_data.get('student_id', '').strip(),
                    current_class=student_data.get('current_class', '').strip(),
                    institute_id=institute.id,
                    created_by=current_user.id
                )
                
                db.add(student)
                created_students.append(student)
                
            except Exception as e:
                errors.append(f"Row {i}: {str(e)}")
        
        if created_students:
            db.commit()
        
        return {
            "message": f"Successfully imported {len(created_students)} students",
            "created_count": len(created_students),
            "error_count": len(errors),
            "errors": errors[:10]  # Return first 10 errors
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}"
        )


# Teacher Management
@router.get("/teachers", response_model=List[TeacherResponseSchema])
async def get_institute_teachers(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    subject: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(True),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Get teachers belonging to the institute"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    query = db.query(Teacher).filter(Teacher.institute_id == institute.id)
    
    # Apply filters
    if search:
        query = query.filter(
            or_(
                Teacher.full_name.ilike(f"%{search}%"),
                Teacher.email.ilike(f"%{search}%"),
                Teacher.employee_id.ilike(f"%{search}%")
            )
        )
    
    if subject:
        query = query.filter(Teacher.subjects.contains([subject]))
    
    if is_active is not None:
        query = query.filter(Teacher.is_active == is_active)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    teachers = query.order_by(Teacher.created_at.desc()).offset(
        (page - 1) * limit
    ).limit(limit).all()
    
    return teachers


@router.post("/teachers", response_model=TeacherResponseSchema)
async def create_teacher(
    teacher_data: TeacherCreateSchema,
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Create new teacher in the institute"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    # Check if employee ID already exists in the institute
    existing_teacher = db.query(Teacher).filter(
        Teacher.institute_id == institute.id,
        Teacher.employee_id == teacher_data.employee_id
    ).first()
    
    if existing_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee ID already exists in this institute"
        )
    
    # Create teacher
    teacher = Teacher(
        **teacher_data.dict(),
        institute_id=institute.id,
        created_by=current_user.id
    )
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return teacher


# Institute Analytics
@router.get("/analytics/performance")
async def get_institute_performance_analytics(
    period: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Get institute performance analytics"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    # Calculate date range
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map[period]
    start_date = datetime.now() - timedelta(days=days)
    
    # Exam performance
    exam_registrations = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.institute_id == institute.id,
        TalentExamRegistration.registration_date >= start_date
    ).all()
    
    # Calculate average scores, pass rates, etc.
    total_registrations = len(exam_registrations)
    completed_exams = [reg for reg in exam_registrations if reg.status == 'completed']
    
    # Student growth
    student_growth = db.query(
        func.date(Student.created_at).label('date'),
        func.count(Student.id).label('count')
    ).filter(
        Student.institute_id == institute.id,
        Student.created_at >= start_date
    ).group_by(func.date(Student.created_at)).all()
    
    return {
        "period": period,
        "exam_performance": {
            "total_registrations": total_registrations,
            "completed_exams": len(completed_exams),
            "completion_rate": len(completed_exams) / total_registrations * 100 if total_registrations > 0 else 0
        },
        "student_growth": [
            {"date": date.isoformat(), "new_students": count}
            for date, count in student_growth
        ],
        "class_wise_performance": {
            # This would include class-wise exam performance
        }
    }


# File Management
@router.post("/files/upload")
async def upload_institute_file(
    file: UploadFile = File(...),
    file_type: str = Query(..., regex="^(student_photo|document|certificate)$"),
    current_user: User = Depends(get_current_user),
    user_context: dict = Depends(get_user_institute_context),
    db: Session = Depends(get_db)
):
    """Upload files for the institute"""
    
    institute = user_context["institute"]
    if not institute:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not associated with any institute"
        )
    
    try:
        # Upload file using file service
        file_url = await file_service.upload_file(
            file,
            f"institutes/{institute.id}/{file_type}/"
        )
        
        return {
            "message": "File uploaded successfully",
            "file_url": file_url,
            "file_type": file_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )
