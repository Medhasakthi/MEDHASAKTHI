"""
School Subject Management API routes for MEDHASAKTHI
Comprehensive subject and curriculum management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_admin_user
from app.models.user import User
from app.models.school_subjects import EducationBoard, ClassLevel, SubjectCategory
from app.services.school_subject_service import school_subject_service

router = APIRouter()


# Subject Management Routes
@router.post("/initialize-default")
async def initialize_default_subjects(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Initialize default subjects for Indian education system"""
    
    result = school_subject_service.initialize_default_subjects(db)
    return {
        "status": "success",
        "data": result
    }


@router.get("/boards")
async def get_education_boards():
    """Get list of supported education boards"""
    
    boards = [
        {
            "code": board.value,
            "name": board.value.replace("_", " ").title(),
            "description": f"{board.value.replace('_', ' ').title()} Education Board"
        }
        for board in EducationBoard
    ]
    
    return {
        "status": "success",
        "data": {
            "boards": boards,
            "total_count": len(boards)
        }
    }


@router.get("/classes")
async def get_class_levels():
    """Get list of supported class levels"""
    
    classes = [
        {
            "code": class_level.value,
            "name": class_level.value.replace("_", " ").title(),
            "display_name": f"Class {class_level.value.split('_')[1]}"
        }
        for class_level in ClassLevel
    ]
    
    return {
        "status": "success",
        "data": {
            "classes": classes,
            "total_count": len(classes)
        }
    }


@router.get("/categories")
async def get_subject_categories():
    """Get list of subject categories"""
    
    categories = [
        {
            "code": category.value,
            "name": category.value.replace("_", " ").title(),
            "description": f"{category.value.replace('_', ' ').title()} subjects"
        }
        for category in SubjectCategory
    ]
    
    return {
        "status": "success",
        "data": {
            "categories": categories,
            "total_count": len(categories)
        }
    }


@router.get("/class/{class_level}/board/{board}")
async def get_subjects_for_class(
    class_level: str,
    board: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subjects for a specific class and board"""
    
    try:
        class_enum = ClassLevel(class_level)
        board_enum = EducationBoard(board)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid class level or board"
        )
    
    subjects = school_subject_service.get_subjects_for_class(
        class_enum, board_enum, db
    )
    
    # Categorize subjects
    categorized_subjects = {
        "mandatory": [s for s in subjects if s["is_mandatory"]],
        "elective": [s for s in subjects if not s["is_mandatory"]]
    }
    
    return {
        "status": "success",
        "data": {
            "class_level": class_level,
            "board": board,
            "subjects": categorized_subjects,
            "total_subjects": len(subjects),
            "mandatory_count": len(categorized_subjects["mandatory"]),
            "elective_count": len(categorized_subjects["elective"])
        }
    }


@router.get("/curriculum/{class_subject_id}")
async def get_subject_curriculum(
    class_subject_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed curriculum for a subject"""
    
    curriculum = school_subject_service.get_subject_curriculum(
        class_subject_id, db
    )
    
    return {
        "status": "success",
        "data": curriculum
    }


# Teacher Assignment Routes
@router.post("/assign-teacher")
async def assign_teacher_to_subject(
    assignment_data: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Assign teacher to subject for specific classes"""
    
    required_fields = ["teacher_id", "subject_id", "institute_id", "class_levels", "academic_year"]
    for field in required_fields:
        if field not in assignment_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    result = school_subject_service.assign_teacher_to_subject(
        teacher_id=assignment_data["teacher_id"],
        subject_id=assignment_data["subject_id"],
        institute_id=assignment_data["institute_id"],
        class_levels=assignment_data["class_levels"],
        academic_year=assignment_data["academic_year"],
        db=db
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/teachers/{institute_id}")
async def get_subject_teachers(
    institute_id: str,
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subject teacher assignments for an institute"""
    
    from app.models.school_subjects import SubjectTeacher, Subject
    from app.models.user import User as UserModel
    
    query = db.query(SubjectTeacher).join(Subject).join(UserModel).filter(
        SubjectTeacher.institute_id == institute_id,
        SubjectTeacher.is_active == True
    )
    
    if academic_year:
        query = query.filter(SubjectTeacher.academic_year == academic_year)
    
    assignments = query.all()
    
    teacher_assignments = []
    for assignment in assignments:
        teacher_data = {
            "assignment_id": str(assignment.id),
            "teacher": {
                "id": str(assignment.teacher_id),
                "name": assignment.teacher.full_name if hasattr(assignment, 'teacher') else "Unknown",
                "email": assignment.teacher.email if hasattr(assignment, 'teacher') else "Unknown"
            },
            "subject": {
                "id": str(assignment.subject.id),
                "name": assignment.subject.name,
                "code": assignment.subject.code
            },
            "class_levels": assignment.class_levels,
            "academic_year": assignment.academic_year,
            "weekly_periods": assignment.weekly_periods,
            "total_students": assignment.total_students
        }
        teacher_assignments.append(teacher_data)
    
    return {
        "status": "success",
        "data": {
            "assignments": teacher_assignments,
            "total_count": len(teacher_assignments),
            "institute_id": institute_id,
            "academic_year": academic_year
        }
    }


# Student Enrollment Routes
@router.post("/enroll-student")
async def enroll_student_in_subjects(
    enrollment_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enroll student in subjects for their class"""
    
    required_fields = ["student_id", "class_level", "board", "academic_year"]
    for field in required_fields:
        if field not in enrollment_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    try:
        class_enum = ClassLevel(enrollment_data["class_level"])
        board_enum = EducationBoard(enrollment_data["board"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid class level or board"
        )
    
    result = school_subject_service.enroll_student_in_subjects(
        student_id=enrollment_data["student_id"],
        class_level=class_enum,
        board=board_enum,
        elective_subjects=enrollment_data.get("elective_subjects", []),
        academic_year=enrollment_data["academic_year"],
        db=db
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/student/{student_id}/subjects")
async def get_student_subjects(
    student_id: str,
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all subjects enrolled by a student"""
    
    from app.models.school_subjects import StudentSubject, ClassSubject, Subject
    
    query = db.query(StudentSubject).join(ClassSubject).join(Subject).filter(
        StudentSubject.student_id == student_id,
        StudentSubject.is_active == True
    )
    
    if academic_year:
        query = query.filter(StudentSubject.academic_year == academic_year)
    
    enrollments = query.all()
    
    student_subjects = []
    for enrollment in enrollments:
        subject_data = {
            "enrollment_id": str(enrollment.id),
            "subject": {
                "id": str(enrollment.class_subject.subject.id),
                "name": enrollment.class_subject.subject.name,
                "code": enrollment.class_subject.subject.code,
                "color": enrollment.class_subject.subject.subject_color
            },
            "class_level": enrollment.class_subject.class_level.value,
            "board": enrollment.class_subject.board.value,
            "is_elective": enrollment.is_elective,
            "academic_year": enrollment.academic_year,
            "current_grade": enrollment.current_grade,
            "attendance_percentage": enrollment.attendance_percentage,
            "assignment_completion": enrollment.assignment_completion,
            "chapters_completed": enrollment.chapters_completed or [],
            "topics_mastered": enrollment.topics_mastered or [],
            "weak_areas": enrollment.weak_areas or []
        }
        student_subjects.append(subject_data)
    
    return {
        "status": "success",
        "data": {
            "subjects": student_subjects,
            "total_count": len(student_subjects),
            "student_id": student_id,
            "academic_year": academic_year
        }
    }


# Curriculum Management Routes
@router.post("/curriculum/chapter")
async def create_subject_chapter(
    chapter_data: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new chapter for a subject"""
    
    from app.models.school_subjects import SubjectChapter
    
    required_fields = ["class_subject_id", "chapter_number", "chapter_name"]
    for field in required_fields:
        if field not in chapter_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    chapter = SubjectChapter(
        class_subject_id=chapter_data["class_subject_id"],
        chapter_number=chapter_data["chapter_number"],
        chapter_name=chapter_data["chapter_name"],
        chapter_description=chapter_data.get("chapter_description"),
        learning_objectives=chapter_data.get("learning_objectives", []),
        key_concepts=chapter_data.get("key_concepts", []),
        estimated_hours=chapter_data.get("estimated_hours", 10),
        difficulty_level=chapter_data.get("difficulty_level", "medium")
    )
    
    db.add(chapter)
    db.commit()
    db.refresh(chapter)
    
    return {
        "status": "success",
        "data": {
            "chapter_id": str(chapter.id),
            "message": "Chapter created successfully"
        }
    }


@router.post("/curriculum/topic")
async def create_chapter_topic(
    topic_data: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new topic for a chapter"""
    
    from app.models.school_subjects import ChapterTopic
    
    required_fields = ["chapter_id", "topic_number", "topic_name"]
    for field in required_fields:
        if field not in topic_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    topic = ChapterTopic(
        chapter_id=topic_data["chapter_id"],
        topic_number=topic_data["topic_number"],
        topic_name=topic_data["topic_name"],
        topic_description=topic_data.get("topic_description"),
        content_type=topic_data.get("content_type", "theory"),
        estimated_time_minutes=topic_data.get("estimated_time_minutes", 45),
        assessment_weightage=topic_data.get("assessment_weightage", 5)
    )
    
    db.add(topic)
    db.commit()
    db.refresh(topic)
    
    return {
        "status": "success",
        "data": {
            "topic_id": str(topic.id),
            "message": "Topic created successfully"
        }
    }


# Analytics and Reports
@router.get("/analytics/institute/{institute_id}")
async def get_subject_analytics(
    institute_id: str,
    academic_year: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get subject-wise analytics for an institute"""
    
    from app.models.school_subjects import StudentSubject, ClassSubject, Subject
    from sqlalchemy import func, and_
    
    # Get subject enrollment statistics
    query = db.query(
        Subject.name,
        Subject.code,
        func.count(StudentSubject.id).label("total_enrollments"),
        func.avg(StudentSubject.attendance_percentage).label("avg_attendance"),
        func.avg(StudentSubject.assignment_completion).label("avg_completion")
    ).join(ClassSubject).join(StudentSubject).filter(
        ClassSubject.id == StudentSubject.class_subject_id,
        StudentSubject.is_active == True
    )
    
    if academic_year:
        query = query.filter(StudentSubject.academic_year == academic_year)
    
    # Filter by institute through student relationship
    from app.models.user import Student
    query = query.join(Student, Student.id == StudentSubject.student_id).filter(
        Student.institute_id == institute_id
    )
    
    results = query.group_by(Subject.name, Subject.code).all()
    
    analytics = []
    for result in results:
        analytics.append({
            "subject_name": result.name,
            "subject_code": result.code,
            "total_enrollments": result.total_enrollments,
            "average_attendance": round(result.avg_attendance or 0, 2),
            "average_completion": round(result.avg_completion or 0, 2)
        })
    
    return {
        "status": "success",
        "data": {
            "analytics": analytics,
            "institute_id": institute_id,
            "academic_year": academic_year,
            "total_subjects": len(analytics)
        }
    }


@router.get("/progress/{student_id}")
async def get_student_progress(
    student_id: str,
    subject_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed progress for a student"""
    
    from app.models.school_subjects import StudentSubject, ClassSubject, Subject, SubjectChapter
    
    query = db.query(StudentSubject).join(ClassSubject).join(Subject).filter(
        StudentSubject.student_id == student_id,
        StudentSubject.is_active == True
    )
    
    if subject_id:
        query = query.filter(Subject.id == subject_id)
    
    enrollments = query.all()
    
    progress_data = []
    for enrollment in enrollments:
        # Get total chapters for the subject
        total_chapters = db.query(SubjectChapter).filter(
            SubjectChapter.class_subject_id == enrollment.class_subject_id
        ).count()
        
        completed_chapters = len(enrollment.chapters_completed or [])
        progress_percentage = (completed_chapters / total_chapters * 100) if total_chapters > 0 else 0
        
        subject_progress = {
            "subject": {
                "id": str(enrollment.class_subject.subject.id),
                "name": enrollment.class_subject.subject.name,
                "code": enrollment.class_subject.subject.code
            },
            "progress_percentage": round(progress_percentage, 2),
            "chapters_completed": completed_chapters,
            "total_chapters": total_chapters,
            "topics_mastered": len(enrollment.topics_mastered or []),
            "weak_areas": enrollment.weak_areas or [],
            "current_grade": enrollment.current_grade,
            "attendance_percentage": enrollment.attendance_percentage,
            "assignment_completion": enrollment.assignment_completion
        }
        progress_data.append(subject_progress)
    
    return {
        "status": "success",
        "data": {
            "student_id": student_id,
            "progress": progress_data,
            "overall_progress": round(sum(p["progress_percentage"] for p in progress_data) / len(progress_data), 2) if progress_data else 0
        }
    }
