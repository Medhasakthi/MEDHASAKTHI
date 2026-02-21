"""
Teacher API routes for MEDHASAKTHI
Comprehensive teacher dashboard and functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_teacher_user
from app.models.user import User
from app.services.teacher_service import teacher_service

router = APIRouter()


@router.get("/dashboard")
async def get_teacher_dashboard(
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive teacher dashboard data"""
    
    dashboard_data = teacher_service.get_teacher_dashboard(
        str(current_user.id), db
    )
    
    return {
        "status": "success",
        "data": dashboard_data
    }


@router.get("/students")
async def get_teacher_students(
    class_filter: Optional[str] = Query(None, description="Filter by class level"),
    section_filter: Optional[str] = Query(None, description="Filter by section"),
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get all students assigned to teacher"""
    
    students = teacher_service.get_teacher_students(
        str(current_user.id), class_filter, section_filter, db
    )
    
    return {
        "status": "success",
        "data": {
            "students": students,
            "total_count": len(students),
            "filters": {
                "class": class_filter,
                "section": section_filter
            }
        }
    }


@router.get("/subjects")
async def get_teacher_subjects(
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get subjects assigned to teacher"""
    
    subjects = teacher_service.get_teacher_subjects(
        str(current_user.id), db
    )
    
    return {
        "status": "success",
        "data": {
            "subjects": subjects,
            "total_count": len(subjects)
        }
    }


@router.get("/classes")
async def get_teacher_classes(
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get classes assigned to teacher"""
    
    from app.models.user import Teacher
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    classes_data = []
    if teacher.classes_assigned:
        for class_info in teacher.classes_assigned:
            classes_data.append({
                "class_level": class_info.get('class'),
                "section": class_info.get('section'),
                "is_class_teacher": (teacher.class_teacher_of == f"{class_info.get('class')}-{class_info.get('section')}")
            })
    
    return {
        "status": "success",
        "data": {
            "classes": classes_data,
            "total_count": len(classes_data),
            "is_class_teacher": teacher.is_class_teacher,
            "class_teacher_of": teacher.class_teacher_of
        }
    }


@router.get("/student/{student_id}/profile")
async def get_student_profile(
    student_id: str,
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get detailed student profile for teacher view"""
    
    from app.models.user import Student, Teacher
    
    # Verify teacher has access to this student
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.institute_id == teacher.institute_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or not accessible"
        )
    
    # Check if teacher has access to this student's class
    has_access = False
    if teacher.classes_assigned:
        for class_info in teacher.classes_assigned:
            if (class_info.get('class') == student.class_level and 
                class_info.get('section') == student.section):
                has_access = True
                break
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this student"
        )
    
    # Get student's exam history
    from app.models.talent_exams import TalentExamRegistration
    exam_history = db.query(TalentExamRegistration).filter(
        TalentExamRegistration.student_id == student.id
    ).order_by(TalentExamRegistration.created_at.desc()).limit(10).all()
    
    student_profile = {
        "basic_info": {
            "id": str(student.id),
            "student_id": student.student_id,
            "name": student.user.full_name,
            "email": student.user.email,
            "class": student.class_level,
            "section": student.section,
            "roll_number": student.roll_number,
            "admission_number": student.admission_number
        },
        "academic_info": {
            "academic_year": student.academic_year,
            "education_board": student.education_board,
            "stream": student.stream,
            "average_score": student.average_score,
            "total_exams": student.total_exams_taken
        },
        "contact_info": {
            "phone": student.phone,
            "guardian_phone": student.guardian_phone,
            "guardian_email": student.guardian_email,
            "emergency_contact": student.emergency_contact_name
        },
        "exam_history": [
            {
                "exam_title": reg.exam.title,
                "exam_date": reg.exam.exam_date.isoformat() if reg.exam.exam_date else None,
                "registration_date": reg.created_at.isoformat(),
                "status": reg.status,
                "score": reg.score if hasattr(reg, 'score') else None
            }
            for reg in exam_history
        ],
        "activity_status": {
            "last_login": student.user.last_login_at.isoformat() if student.user.last_login_at else None,
            "first_login_completed": student.first_login_completed,
            "password_changed": student.default_password_changed,
            "is_active": student.is_active
        }
    }
    
    return {
        "status": "success",
        "data": student_profile
    }


@router.post("/student/{student_id}/message")
async def send_message_to_student(
    student_id: str,
    message_data: Dict[str, str],
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Send message to student"""
    
    from app.models.user import Student, Teacher
    from app.services.email_service import email_service
    
    # Verify teacher has access to this student
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    student = db.query(Student).filter(
        Student.student_id == student_id,
        Student.institute_id == teacher.institute_id
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check access
    has_access = False
    if teacher.classes_assigned:
        for class_info in teacher.classes_assigned:
            if (class_info.get('class') == student.class_level and 
                class_info.get('section') == student.section):
                has_access = True
                break
    
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this student"
        )
    
    # Send message via email
    try:
        subject = message_data.get('subject', 'Message from Teacher')
        message = message_data.get('message', '')
        
        email_content = f"""
        Dear {student.user.full_name},

        You have received a message from your teacher {teacher.user.full_name}:

        Subject: {subject}

        Message:
        {message}

        Best regards,
        {teacher.user.full_name}
        {teacher.designation or 'Teacher'}
        {teacher.institute.name if teacher.institute else ''}
        """
        
        # Send to student and guardian if available
        recipients = [student.user.email]
        if student.guardian_email:
            recipients.append(student.guardian_email)
        
        for recipient in recipients:
            email_service.send_email(
                to_email=recipient,
                subject=f"Message from Teacher - {subject}",
                content=email_content
            )
        
        return {
            "status": "success",
            "message": "Message sent successfully",
            "data": {
                "recipients": recipients,
                "subject": subject
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.get("/analytics/class-performance")
async def get_class_performance_analytics(
    class_level: Optional[str] = Query(None),
    section: Optional[str] = Query(None),
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get class performance analytics"""
    
    from app.models.user import Teacher, Student
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    analytics_data = []
    
    # Get performance data for teacher's classes
    if teacher.classes_assigned:
        for class_info in teacher.classes_assigned:
            cls = class_info.get('class')
            sec = class_info.get('section')
            
            # Apply filters
            if class_level and cls != class_level:
                continue
            if section and sec != section:
                continue
            
            students = db.query(Student).filter(
                Student.institute_id == teacher.institute_id,
                Student.class_level == cls,
                Student.section == sec,
                Student.is_active == True
            ).all()
            
            if students:
                avg_score = sum(s.average_score for s in students) / len(students)
                total_exams = sum(s.total_exams_taken for s in students)
                
                analytics_data.append({
                    "class": cls,
                    "section": sec,
                    "total_students": len(students),
                    "average_score": round(avg_score, 2),
                    "total_exams_taken": total_exams,
                    "performance_trend": "+5.2%",  # Mock data
                    "top_performers": [
                        {
                            "name": s.user.full_name,
                            "score": s.average_score
                        }
                        for s in sorted(students, key=lambda x: x.average_score, reverse=True)[:3]
                    ]
                })
    
    return {
        "status": "success",
        "data": {
            "analytics": analytics_data,
            "filters": {
                "class_level": class_level,
                "section": section
            }
        }
    }


@router.get("/profile")
async def get_teacher_profile(
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Get teacher's own profile"""
    
    from app.models.user import Teacher
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    profile_data = {
        "basic_info": {
            "id": str(teacher.id),
            "teacher_id": teacher.teacher_id,
            "employee_id": teacher.employee_id,
            "name": teacher.user.full_name,
            "email": teacher.user.email,
            "phone": teacher.phone,
            "address": teacher.address
        },
        "professional_info": {
            "subject_specialization": teacher.subject_specialization,
            "qualifications": teacher.qualifications,
            "experience_years": teacher.experience_years,
            "designation": teacher.designation,
            "department": teacher.department,
            "joining_date": teacher.joining_date.isoformat() if teacher.joining_date else None
        },
        "teaching_assignment": {
            "classes_assigned": teacher.classes_assigned,
            "subjects_assigned": teacher.subjects_assigned,
            "is_class_teacher": teacher.is_class_teacher,
            "class_teacher_of": teacher.class_teacher_of
        },
        "contact_info": {
            "office_phone": teacher.office_phone,
            "office_location": teacher.office_location,
            "emergency_contact_name": teacher.emergency_contact_name,
            "emergency_contact_phone": teacher.emergency_contact_phone
        },
        "account_status": {
            "is_active": teacher.is_active,
            "first_login_completed": teacher.first_login_completed,
            "password_changed": teacher.default_password_changed,
            "last_login": teacher.user.last_login_at.isoformat() if teacher.user.last_login_at else None
        }
    }
    
    return {
        "status": "success",
        "data": profile_data
    }


@router.put("/profile")
async def update_teacher_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_teacher_user),
    db: Session = Depends(get_db)
):
    """Update teacher profile"""
    
    from app.models.user import Teacher
    
    teacher = db.query(Teacher).filter(Teacher.user_id == current_user.id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found"
        )
    
    # Update allowed fields
    updatable_fields = [
        'phone', 'address', 'office_phone', 'office_location',
        'emergency_contact_name', 'emergency_contact_phone'
    ]
    
    for field in updatable_fields:
        if field in profile_data:
            setattr(teacher, field, profile_data[field])
    
    # Update user fields
    if 'full_name' in profile_data:
        teacher.user.full_name = profile_data['full_name']
    
    try:
        db.commit()
        return {
            "status": "success",
            "message": "Profile updated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )
