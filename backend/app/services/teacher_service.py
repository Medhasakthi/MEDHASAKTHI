"""
Teacher Service for MEDHASAKTHI
Comprehensive teacher dashboard and functionality management
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.models.user import User, Teacher, Student, Institute
from app.models.school_subjects import ClassSubject, StudentSubject, SubjectTeacher
from app.models.talent_exam import TalentExam, TalentExamRegistration


class TeacherService:
    """Service for teacher-specific operations and dashboard"""
    
    def get_teacher_dashboard(self, teacher_id: str, db: Session) -> Dict[str, Any]:
        """Get comprehensive teacher dashboard data"""
        
        teacher = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher profile not found"
            )
        
        # Get basic statistics
        stats = self._get_teacher_stats(teacher, db)
        
        # Get assigned classes and students
        classes_info = self._get_assigned_classes(teacher, db)
        
        # Get recent activities
        recent_activities = self._get_recent_activities(teacher, db)
        
        # Get upcoming events
        upcoming_events = self._get_upcoming_events(teacher, db)
        
        # Get performance analytics
        performance_data = self._get_performance_analytics(teacher, db)
        
        return {
            "teacher_info": {
                "id": str(teacher.id),
                "teacher_id": teacher.teacher_id,
                "name": teacher.user.full_name,
                "email": teacher.user.email,
                "subject_specialization": teacher.subject_specialization,
                "designation": teacher.designation,
                "department": teacher.department,
                "experience_years": teacher.experience_years,
                "is_class_teacher": teacher.is_class_teacher,
                "class_teacher_of": teacher.class_teacher_of
            },
            "statistics": stats,
            "classes_info": classes_info,
            "recent_activities": recent_activities,
            "upcoming_events": upcoming_events,
            "performance_analytics": performance_data
        }
    
    def _get_teacher_stats(self, teacher: Teacher, db: Session) -> Dict[str, Any]:
        """Get teacher statistics"""
        
        # Count assigned students
        total_students = 0
        if teacher.classes_assigned:
            for class_info in teacher.classes_assigned:
                class_students = db.query(Student).filter(
                    and_(
                        Student.institute_id == teacher.institute_id,
                        Student.class_level == class_info.get('class'),
                        Student.section == class_info.get('section'),
                        Student.is_active == True
                    )
                ).count()
                total_students += class_students
        
        # Count subjects taught
        subjects_count = len(teacher.subjects_assigned) if teacher.subjects_assigned else 0
        
        # Count classes handled
        classes_count = len(teacher.classes_assigned) if teacher.classes_assigned else 0
        
        # Get recent exam statistics
        recent_exams = db.query(TalentExam).filter(
            and_(
                TalentExam.institute_id == teacher.institute_id,
                TalentExam.created_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).count()
        
        return {
            "total_students": total_students,
            "subjects_taught": subjects_count,
            "classes_handled": classes_count,
            "recent_exams": recent_exams,
            "experience_years": teacher.experience_years,
            "is_class_teacher": teacher.is_class_teacher
        }
    
    def _get_assigned_classes(self, teacher: Teacher, db: Session) -> List[Dict[str, Any]]:
        """Get detailed information about assigned classes"""
        
        classes_info = []
        
        if teacher.classes_assigned:
            for class_info in teacher.classes_assigned:
                class_level = class_info.get('class')
                section = class_info.get('section')
                
                # Get students in this class
                students = db.query(Student).filter(
                    and_(
                        Student.institute_id == teacher.institute_id,
                        Student.class_level == class_level,
                        Student.section == section,
                        Student.is_active == True
                    )
                ).all()
                
                # Get subjects for this class
                class_subjects = db.query(ClassSubject).filter(
                    and_(
                        ClassSubject.class_level == class_level,
                        ClassSubject.is_active == True
                    )
                ).all()
                
                class_data = {
                    "class_level": class_level,
                    "section": section,
                    "total_students": len(students),
                    "is_class_teacher": (teacher.class_teacher_of == f"{class_level}-{section}"),
                    "subjects": [
                        {
                            "id": str(cs.id),
                            "name": cs.subject.name,
                            "code": cs.subject.code
                        }
                        for cs in class_subjects
                    ],
                    "students": [
                        {
                            "id": str(s.id),
                            "student_id": s.student_id,
                            "name": s.user.full_name,
                            "roll_number": s.roll_number
                        }
                        for s in students[:10]  # Limit to first 10 for dashboard
                    ]
                }
                classes_info.append(class_data)
        
        return classes_info
    
    def _get_recent_activities(self, teacher: Teacher, db: Session) -> List[Dict[str, Any]]:
        """Get recent teacher activities"""
        
        activities = []
        
        # Recent logins
        if teacher.user.last_login_at:
            activities.append({
                "type": "login",
                "description": "Last login to platform",
                "timestamp": teacher.user.last_login_at.isoformat(),
                "icon": "login"
            })
        
        # Recent exam registrations (if any students registered for exams)
        recent_registrations = db.query(TalentExamRegistration).join(Student).filter(
            and_(
                Student.institute_id == teacher.institute_id,
                TalentExamRegistration.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        ).order_by(desc(TalentExamRegistration.created_at)).limit(5).all()
        
        for reg in recent_registrations:
            activities.append({
                "type": "exam_registration",
                "description": f"Student {reg.student.user.full_name} registered for {reg.exam.title}",
                "timestamp": reg.created_at.isoformat(),
                "icon": "exam"
            })
        
        # Sort activities by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activities[:10]  # Return latest 10 activities
    
    def _get_upcoming_events(self, teacher: Teacher, db: Session) -> List[Dict[str, Any]]:
        """Get upcoming events relevant to teacher"""
        
        events = []
        
        # Upcoming exams
        upcoming_exams = db.query(TalentExam).filter(
            and_(
                TalentExam.institute_id == teacher.institute_id,
                TalentExam.exam_date >= datetime.utcnow().date(),
                TalentExam.status == "scheduled"
            )
        ).order_by(TalentExam.exam_date).limit(5).all()
        
        for exam in upcoming_exams:
            events.append({
                "type": "exam",
                "title": exam.title,
                "description": f"Talent exam for {exam.target_class}",
                "date": exam.exam_date.isoformat(),
                "time": exam.start_time.isoformat() if exam.start_time else None,
                "priority": "high"
            })
        
        # Add mock events for demonstration
        events.extend([
            {
                "type": "meeting",
                "title": "Staff Meeting",
                "description": "Monthly staff meeting",
                "date": (datetime.utcnow() + timedelta(days=3)).date().isoformat(),
                "time": "10:00:00",
                "priority": "medium"
            },
            {
                "type": "training",
                "title": "MEDHASAKTHI Training",
                "description": "Platform training session",
                "date": (datetime.utcnow() + timedelta(days=7)).date().isoformat(),
                "time": "14:00:00",
                "priority": "low"
            }
        ])
        
        return events
    
    def _get_performance_analytics(self, teacher: Teacher, db: Session) -> Dict[str, Any]:
        """Get teacher performance analytics"""
        
        # Get student performance data for teacher's classes
        performance_data = {
            "class_performance": [],
            "subject_performance": [],
            "monthly_trends": [],
            "improvement_areas": []
        }
        
        if teacher.classes_assigned:
            for class_info in teacher.classes_assigned:
                class_level = class_info.get('class')
                section = class_info.get('section')
                
                # Get average performance for this class
                students = db.query(Student).filter(
                    and_(
                        Student.institute_id == teacher.institute_id,
                        Student.class_level == class_level,
                        Student.section == section,
                        Student.is_active == True
                    )
                ).all()
                
                if students:
                    avg_score = sum(s.average_score for s in students) / len(students)
                    performance_data["class_performance"].append({
                        "class": f"{class_level}-{section}",
                        "average_score": round(avg_score, 2),
                        "total_students": len(students),
                        "improvement": "+5.2%"  # Mock data
                    })
        
        # Mock subject performance data
        if teacher.subjects_assigned:
            for subject in teacher.subjects_assigned:
                performance_data["subject_performance"].append({
                    "subject": subject,
                    "average_score": 78.5,  # Mock data
                    "completion_rate": 92.3,  # Mock data
                    "difficulty_rating": "Medium"
                })
        
        # Mock monthly trends
        performance_data["monthly_trends"] = [
            {"month": "Jan", "score": 75.2},
            {"month": "Feb", "score": 77.8},
            {"month": "Mar", "score": 79.1},
            {"month": "Apr", "score": 81.3},
            {"month": "May", "score": 83.7}
        ]
        
        # Mock improvement areas
        performance_data["improvement_areas"] = [
            {
                "area": "Mathematics Problem Solving",
                "current_score": 72.5,
                "target_score": 80.0,
                "priority": "High"
            },
            {
                "area": "Science Practical Knowledge",
                "current_score": 78.2,
                "target_score": 85.0,
                "priority": "Medium"
            }
        ]
        
        return performance_data
    
    def get_teacher_students(
        self, 
        teacher_id: str, 
        class_filter: Optional[str] = None,
        section_filter: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get all students assigned to teacher"""
        
        teacher = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher profile not found"
            )
        
        students_data = []
        
        if teacher.classes_assigned:
            for class_info in teacher.classes_assigned:
                class_level = class_info.get('class')
                section = class_info.get('section')
                
                # Apply filters if provided
                if class_filter and class_level != class_filter:
                    continue
                if section_filter and section != section_filter:
                    continue
                
                students = db.query(Student).filter(
                    and_(
                        Student.institute_id == teacher.institute_id,
                        Student.class_level == class_level,
                        Student.section == section,
                        Student.is_active == True
                    )
                ).all()
                
                for student in students:
                    students_data.append({
                        "id": str(student.id),
                        "student_id": student.student_id,
                        "name": student.user.full_name,
                        "email": student.user.email,
                        "class": class_level,
                        "section": section,
                        "roll_number": student.roll_number,
                        "average_score": student.average_score,
                        "total_exams": student.total_exams_taken,
                        "last_login": student.user.last_login_at.isoformat() if student.user.last_login_at else None,
                        "is_active": student.is_active
                    })
        
        return students_data
    
    def get_teacher_subjects(self, teacher_id: str, db: Session) -> List[Dict[str, Any]]:
        """Get subjects assigned to teacher"""
        
        teacher = db.query(Teacher).filter(Teacher.user_id == teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Teacher profile not found"
            )
        
        subjects_data = []
        
        if teacher.subjects_assigned:
            for subject_name in teacher.subjects_assigned:
                # Get subject details from ClassSubject
                class_subjects = db.query(ClassSubject).join(
                    ClassSubject.subject
                ).filter(
                    ClassSubject.subject.has(name=subject_name)
                ).all()
                
                if class_subjects:
                    subject_info = {
                        "name": subject_name,
                        "classes": [],
                        "total_students": 0,
                        "average_performance": 0
                    }
                    
                    for cs in class_subjects:
                        # Count students in this class-subject
                        student_count = db.query(StudentSubject).filter(
                            StudentSubject.class_subject_id == cs.id
                        ).count()
                        
                        subject_info["classes"].append({
                            "class_level": cs.class_level.value,
                            "student_count": student_count
                        })
                        subject_info["total_students"] += student_count
                    
                    subjects_data.append(subject_info)
        
        return subjects_data


# Global instance
teacher_service = TeacherService()
