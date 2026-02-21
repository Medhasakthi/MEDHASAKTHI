"""
School Subject Management Service for MEDHASAKTHI
Comprehensive service for managing class-wise subjects across education boards
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status

from app.models.school_subjects import (
    Subject, BoardSubject, ClassSubject, SubjectChapter, ChapterTopic,
    SubjectTeacher, StudentSubject, SubjectAssessment,
    EducationBoard, ClassLevel, SubjectCategory
)
from app.models.user import Institute, Student


class SchoolSubjectService:
    """Service for managing school subjects and curriculum"""
    
    def __init__(self):
        self.indian_curriculum_data = self._load_indian_curriculum_data()
    
    def initialize_default_subjects(self, db: Session) -> Dict[str, Any]:
        """Initialize default subjects for Indian education system"""
        
        created_subjects = []
        
        # Core subjects for all boards
        core_subjects = [
            {
                "name": "Mathematics", "code": "MATH", "category": SubjectCategory.CORE,
                "is_core_subject": True, "theory_marks": 100, "subject_color": "#FF6B6B"
            },
            {
                "name": "Science", "code": "SCI", "category": SubjectCategory.CORE,
                "is_core_subject": True, "theory_marks": 100, "practical_marks": 20, "subject_color": "#4ECDC4"
            },
            {
                "name": "English", "code": "ENG", "category": SubjectCategory.LANGUAGE,
                "is_core_subject": True, "is_language": True, "theory_marks": 100, "subject_color": "#45B7D1"
            },
            {
                "name": "Hindi", "code": "HIN", "category": SubjectCategory.LANGUAGE,
                "is_language": True, "theory_marks": 100, "subject_color": "#96CEB4"
            },
            {
                "name": "Social Science", "code": "SST", "category": SubjectCategory.CORE,
                "is_core_subject": True, "theory_marks": 100, "subject_color": "#FFEAA7"
            },
            {
                "name": "Environmental Studies", "code": "EVS", "category": SubjectCategory.CORE,
                "theory_marks": 50, "subject_color": "#DDA0DD"
            }
        ]
        
        # Secondary level subjects
        secondary_subjects = [
            {
                "name": "Physics", "code": "PHY", "category": SubjectCategory.CORE,
                "theory_marks": 70, "practical_marks": 30, "requires_practical": True, "subject_color": "#FF7675"
            },
            {
                "name": "Chemistry", "code": "CHE", "category": SubjectCategory.CORE,
                "theory_marks": 70, "practical_marks": 30, "requires_practical": True, "subject_color": "#74B9FF"
            },
            {
                "name": "Biology", "code": "BIO", "category": SubjectCategory.CORE,
                "theory_marks": 70, "practical_marks": 30, "requires_practical": True, "subject_color": "#00B894"
            },
            {
                "name": "History", "code": "HIS", "category": SubjectCategory.CORE,
                "theory_marks": 100, "subject_color": "#FDCB6E"
            },
            {
                "name": "Geography", "code": "GEO", "category": SubjectCategory.CORE,
                "theory_marks": 100, "subject_color": "#E17055"
            },
            {
                "name": "Political Science", "code": "POL", "category": SubjectCategory.CORE,
                "theory_marks": 100, "subject_color": "#A29BFE"
            },
            {
                "name": "Economics", "code": "ECO", "category": SubjectCategory.CORE,
                "theory_marks": 100, "subject_color": "#FD79A8"
            }
        ]
        
        # Elective subjects
        elective_subjects = [
            {
                "name": "Computer Science", "code": "CS", "category": SubjectCategory.ELECTIVE,
                "theory_marks": 70, "practical_marks": 30, "requires_practical": True, "subject_color": "#6C5CE7"
            },
            {
                "name": "Physical Education", "code": "PE", "category": SubjectCategory.ELECTIVE,
                "theory_marks": 70, "practical_marks": 30, "subject_color": "#00CEC9"
            },
            {
                "name": "Fine Arts", "code": "FA", "category": SubjectCategory.ELECTIVE,
                "theory_marks": 100, "subject_color": "#FF7675"
            },
            {
                "name": "Music", "code": "MUS", "category": SubjectCategory.ELECTIVE,
                "theory_marks": 100, "subject_color": "#FDCB6E"
            },
            {
                "name": "Sanskrit", "code": "SAN", "category": SubjectCategory.LANGUAGE,
                "is_language": True, "theory_marks": 100, "subject_color": "#E17055"
            }
        ]
        
        all_subjects = core_subjects + secondary_subjects + elective_subjects
        
        for subject_data in all_subjects:
            # Check if subject already exists
            existing = db.query(Subject).filter(Subject.code == subject_data["code"]).first()
            if not existing:
                subject = Subject(**subject_data)
                db.add(subject)
                created_subjects.append(subject_data["name"])
        
        db.commit()
        
        # Initialize board-specific configurations
        self._initialize_board_subjects(db)
        
        # Initialize class-subject mappings
        self._initialize_class_subjects(db)
        
        return {
            "created_subjects": created_subjects,
            "total_subjects": len(all_subjects),
            "message": "Default subjects initialized successfully"
        }
    
    def _initialize_board_subjects(self, db: Session):
        """Initialize board-specific subject configurations"""
        
        subjects = db.query(Subject).all()
        boards = [EducationBoard.CBSE, EducationBoard.ICSE, EducationBoard.STATE_BOARD]
        
        for board in boards:
            for subject in subjects:
                existing = db.query(BoardSubject).filter(
                    and_(BoardSubject.board == board, BoardSubject.subject_id == subject.id)
                ).first()
                
                if not existing:
                    board_subject = BoardSubject(
                        board=board,
                        subject_id=subject.id,
                        board_subject_code=f"{board.value.upper()}_{subject.code}",
                        board_subject_name=subject.name,
                        is_compulsory=subject.is_core_subject,
                        passing_marks=35 if subject.theory_marks >= 100 else 20,
                        grading_scheme=self._get_board_grading_scheme(board)
                    )
                    db.add(board_subject)
        
        db.commit()
    
    def _initialize_class_subjects(self, db: Session):
        """Initialize class-wise subject mappings"""
        
        subjects = db.query(Subject).all()
        subject_map = {s.code: s for s in subjects}
        
        # Class-wise subject allocation
        class_subject_mapping = {
            ClassLevel.CLASS_1: ["ENG", "HIN", "MATH", "EVS"],
            ClassLevel.CLASS_2: ["ENG", "HIN", "MATH", "EVS"],
            ClassLevel.CLASS_3: ["ENG", "HIN", "MATH", "EVS", "SCI"],
            ClassLevel.CLASS_4: ["ENG", "HIN", "MATH", "EVS", "SCI"],
            ClassLevel.CLASS_5: ["ENG", "HIN", "MATH", "EVS", "SCI"],
            ClassLevel.CLASS_6: ["ENG", "HIN", "MATH", "SCI", "SST"],
            ClassLevel.CLASS_7: ["ENG", "HIN", "MATH", "SCI", "SST"],
            ClassLevel.CLASS_8: ["ENG", "HIN", "MATH", "SCI", "SST"],
            ClassLevel.CLASS_9: ["ENG", "HIN", "MATH", "SCI", "SST", "CS", "PE"],
            ClassLevel.CLASS_10: ["ENG", "HIN", "MATH", "SCI", "SST", "CS", "PE"],
            ClassLevel.CLASS_11: ["ENG", "MATH", "PHY", "CHE", "BIO", "HIS", "GEO", "POL", "ECO", "CS", "PE"],
            ClassLevel.CLASS_12: ["ENG", "MATH", "PHY", "CHE", "BIO", "HIS", "GEO", "POL", "ECO", "CS", "PE"]
        }
        
        boards = [EducationBoard.CBSE, EducationBoard.ICSE, EducationBoard.STATE_BOARD]
        
        for class_level, subject_codes in class_subject_mapping.items():
            for board in boards:
                for subject_code in subject_codes:
                    if subject_code in subject_map:
                        subject = subject_map[subject_code]
                        
                        existing = db.query(ClassSubject).filter(
                            and_(
                                ClassSubject.class_level == class_level,
                                ClassSubject.subject_id == subject.id,
                                ClassSubject.board == board
                            )
                        ).first()
                        
                        if not existing:
                            is_mandatory = subject.is_core_subject or subject_code in ["ENG", "HIN", "MATH"]
                            
                            class_subject = ClassSubject(
                                class_level=class_level,
                                subject_id=subject.id,
                                board=board,
                                is_mandatory=is_mandatory,
                                weekly_periods=self._get_weekly_periods(class_level, subject_code),
                                annual_hours=self._get_annual_hours(class_level, subject_code),
                                assessment_pattern=self._get_assessment_pattern(class_level, subject_code),
                                project_required=subject_code in ["CS", "SCI", "EVS"],
                                lab_required=subject.requires_practical
                            )
                            db.add(class_subject)
        
        db.commit()
    
    def get_subjects_for_class(
        self, 
        class_level: ClassLevel, 
        board: EducationBoard, 
        db: Session
    ) -> List[Dict[str, Any]]:
        """Get all subjects for a specific class and board"""
        
        class_subjects = db.query(ClassSubject).join(Subject).filter(
            and_(
                ClassSubject.class_level == class_level,
                ClassSubject.board == board,
                ClassSubject.is_active == True,
                Subject.is_active == True
            )
        ).all()
        
        subjects = []
        for cs in class_subjects:
            subject_data = {
                "id": str(cs.subject.id),
                "name": cs.subject.name,
                "code": cs.subject.code,
                "category": cs.subject.category.value,
                "is_mandatory": cs.is_mandatory,
                "weekly_periods": cs.weekly_periods,
                "annual_hours": cs.annual_hours,
                "theory_marks": cs.subject.theory_marks,
                "practical_marks": cs.subject.practical_marks,
                "requires_practical": cs.subject.requires_practical,
                "project_required": cs.project_required,
                "lab_required": cs.lab_required,
                "subject_color": cs.subject.subject_color,
                "assessment_pattern": cs.assessment_pattern
            }
            subjects.append(subject_data)
        
        return subjects
    
    def get_subject_curriculum(
        self, 
        class_subject_id: str, 
        db: Session
    ) -> Dict[str, Any]:
        """Get detailed curriculum for a subject"""
        
        class_subject = db.query(ClassSubject).filter(
            ClassSubject.id == class_subject_id
        ).first()
        
        if not class_subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        chapters = db.query(SubjectChapter).filter(
            SubjectChapter.class_subject_id == class_subject_id
        ).order_by(SubjectChapter.chapter_number).all()
        
        curriculum = {
            "subject": {
                "id": str(class_subject.subject.id),
                "name": class_subject.subject.name,
                "code": class_subject.subject.code,
                "class_level": class_subject.class_level.value,
                "board": class_subject.board.value
            },
            "chapters": []
        }
        
        for chapter in chapters:
            topics = db.query(ChapterTopic).filter(
                ChapterTopic.chapter_id == chapter.id
            ).order_by(ChapterTopic.topic_number).all()
            
            chapter_data = {
                "id": str(chapter.id),
                "chapter_number": chapter.chapter_number,
                "chapter_name": chapter.chapter_name,
                "description": chapter.chapter_description,
                "learning_objectives": chapter.learning_objectives,
                "key_concepts": chapter.key_concepts,
                "estimated_hours": chapter.estimated_hours,
                "difficulty_level": chapter.difficulty_level,
                "topics": [
                    {
                        "id": str(topic.id),
                        "topic_number": topic.topic_number,
                        "topic_name": topic.topic_name,
                        "description": topic.topic_description,
                        "content_type": topic.content_type,
                        "estimated_time_minutes": topic.estimated_time_minutes,
                        "assessment_weightage": topic.assessment_weightage
                    }
                    for topic in topics
                ]
            }
            curriculum["chapters"].append(chapter_data)
        
        return curriculum
    
    def assign_teacher_to_subject(
        self,
        teacher_id: str,
        subject_id: str,
        institute_id: str,
        class_levels: List[str],
        academic_year: str,
        db: Session
    ) -> Dict[str, Any]:
        """Assign teacher to subject for specific classes"""
        
        # Check if assignment already exists
        existing = db.query(SubjectTeacher).filter(
            and_(
                SubjectTeacher.teacher_id == teacher_id,
                SubjectTeacher.subject_id == subject_id,
                SubjectTeacher.institute_id == institute_id,
                SubjectTeacher.academic_year == academic_year
            )
        ).first()
        
        if existing:
            # Update existing assignment
            existing.class_levels = class_levels
            existing.is_active = True
            db.commit()
            return {"message": "Teacher assignment updated", "assignment_id": str(existing.id)}
        else:
            # Create new assignment
            assignment = SubjectTeacher(
                teacher_id=teacher_id,
                subject_id=subject_id,
                institute_id=institute_id,
                class_levels=class_levels,
                academic_year=academic_year
            )
            db.add(assignment)
            db.commit()
            db.refresh(assignment)
            
            return {"message": "Teacher assigned successfully", "assignment_id": str(assignment.id)}
    
    def enroll_student_in_subjects(
        self,
        student_id: str,
        class_level: ClassLevel,
        board: EducationBoard,
        elective_subjects: List[str],
        academic_year: str,
        db: Session
    ) -> Dict[str, Any]:
        """Enroll student in mandatory and selected elective subjects"""
        
        # Get all subjects for the class
        class_subjects = db.query(ClassSubject).filter(
            and_(
                ClassSubject.class_level == class_level,
                ClassSubject.board == board,
                ClassSubject.is_active == True
            )
        ).all()
        
        enrolled_subjects = []
        
        for cs in class_subjects:
            # Enroll in mandatory subjects or selected electives
            if cs.is_mandatory or str(cs.subject.id) in elective_subjects:
                existing = db.query(StudentSubject).filter(
                    and_(
                        StudentSubject.student_id == student_id,
                        StudentSubject.class_subject_id == cs.id,
                        StudentSubject.academic_year == academic_year
                    )
                ).first()
                
                if not existing:
                    enrollment = StudentSubject(
                        student_id=student_id,
                        class_subject_id=cs.id,
                        academic_year=academic_year,
                        is_elective=not cs.is_mandatory
                    )
                    db.add(enrollment)
                    enrolled_subjects.append(cs.subject.name)
        
        db.commit()
        
        return {
            "enrolled_subjects": enrolled_subjects,
            "total_subjects": len(enrolled_subjects),
            "message": "Student enrolled in subjects successfully"
        }
    
    def _get_board_grading_scheme(self, board: EducationBoard) -> Dict[str, Any]:
        """Get grading scheme for specific board"""
        
        if board == EducationBoard.CBSE:
            return {
                "grades": {
                    "A1": {"min": 91, "max": 100, "grade_point": 10},
                    "A2": {"min": 81, "max": 90, "grade_point": 9},
                    "B1": {"min": 71, "max": 80, "grade_point": 8},
                    "B2": {"min": 61, "max": 70, "grade_point": 7},
                    "C1": {"min": 51, "max": 60, "grade_point": 6},
                    "C2": {"min": 41, "max": 50, "grade_point": 5},
                    "D": {"min": 33, "max": 40, "grade_point": 4},
                    "E": {"min": 0, "max": 32, "grade_point": 0}
                }
            }
        elif board == EducationBoard.ICSE:
            return {
                "grades": {
                    "A": {"min": 85, "max": 100},
                    "B": {"min": 70, "max": 84},
                    "C": {"min": 55, "max": 69},
                    "D": {"min": 40, "max": 54},
                    "F": {"min": 0, "max": 39}
                }
            }
        else:
            return {
                "grades": {
                    "A+": {"min": 90, "max": 100},
                    "A": {"min": 80, "max": 89},
                    "B+": {"min": 70, "max": 79},
                    "B": {"min": 60, "max": 69},
                    "C": {"min": 50, "max": 59},
                    "D": {"min": 35, "max": 49},
                    "F": {"min": 0, "max": 34}
                }
            }
    
    def _get_weekly_periods(self, class_level: ClassLevel, subject_code: str) -> int:
        """Get weekly periods for subject based on class"""
        
        period_mapping = {
            "MATH": 6, "SCI": 5, "ENG": 5, "HIN": 4, "SST": 4,
            "PHY": 5, "CHE": 5, "BIO": 5, "CS": 4, "PE": 2,
            "EVS": 3, "HIS": 3, "GEO": 3, "POL": 3, "ECO": 3
        }
        
        return period_mapping.get(subject_code, 3)
    
    def _get_annual_hours(self, class_level: ClassLevel, subject_code: str) -> int:
        """Get annual hours for subject"""
        
        weekly_periods = self._get_weekly_periods(class_level, subject_code)
        return weekly_periods * 40  # Assuming 40 weeks in academic year
    
    def _get_assessment_pattern(self, class_level: ClassLevel, subject_code: str) -> Dict[str, Any]:
        """Get assessment pattern for subject"""
        
        if class_level in [ClassLevel.CLASS_1, ClassLevel.CLASS_2]:
            return {
                "continuous_assessment": 100,
                "term_exam": 0,
                "project": 0
            }
        elif class_level in [ClassLevel.CLASS_3, ClassLevel.CLASS_4, ClassLevel.CLASS_5]:
            return {
                "continuous_assessment": 60,
                "term_exam": 40,
                "project": 0
            }
        else:
            return {
                "continuous_assessment": 20,
                "term_exam": 80,
                "project": 10 if subject_code in ["CS", "SCI", "EVS"] else 0
            }
    
    def _load_indian_curriculum_data(self) -> Dict[str, Any]:
        """Load comprehensive Indian curriculum data"""
        
        return {
            "boards": ["CBSE", "ICSE", "State Board", "IB", "Cambridge"],
            "class_levels": [f"Class {i}" for i in range(1, 13)],
            "core_subjects": ["Mathematics", "Science", "English", "Hindi", "Social Science"],
            "elective_subjects": ["Computer Science", "Physical Education", "Fine Arts", "Music", "Sanskrit"]
        }


# Global instance
school_subject_service = SchoolSubjectService()
