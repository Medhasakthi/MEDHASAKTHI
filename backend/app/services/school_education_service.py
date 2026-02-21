"""
School Education Service for MEDHASAKTHI
Manages school-level education system with subjects, curricula, and academic structure
"""
import uuid
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.school_education import (
    SchoolSubject, SchoolTopic, SchoolCurriculum, SchoolAcademicYear,
    SchoolGradingSystem, EducationBoard, EducationLevel, Stream, MediumOfInstruction
)
from app.utils.indian_education_system import INDIAN_EDUCATION_SYSTEM, INDIAN_EDUCATION_BOARDS


class SchoolEducationService:
    """Service for managing school education system"""
    
    def __init__(self):
        self.current_academic_year = self._get_current_academic_year()
    
    def _get_current_academic_year(self) -> str:
        """Get current academic year (e.g., 2024-25)"""
        from datetime import datetime
        now = datetime.now()
        if now.month >= 4:  # April onwards is new academic year
            return f"{now.year}-{str(now.year + 1)[2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[2:]}"
    
    async def initialize_school_subjects(self, db: Session) -> Tuple[bool, str]:
        """Initialize school subjects for all boards and classes"""
        
        try:
            # CBSE Subjects
            await self._create_cbse_subjects(db)
            
            # ICSE Subjects  
            await self._create_icse_subjects(db)
            
            # State Board Subjects (sample for major states)
            await self._create_state_board_subjects(db)
            
            db.commit()
            return True, "School subjects initialized successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error initializing school subjects: {str(e)}"
    
    async def _create_cbse_subjects(self, db: Session):
        """Create CBSE subjects for all classes"""
        
        # Primary Classes (1-5)
        primary_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True},
            {"name": "Hindi", "code": "HIN", "category": "Language", "core": True},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": True},
            {"name": "Environmental Studies", "code": "EVS", "category": "Science", "core": True},
            {"name": "Art Education", "code": "ART", "category": "Arts", "core": False},
            {"name": "Physical Education", "code": "PE", "category": "Physical", "core": False}
        ]
        
        for class_num in range(1, 6):
            class_level = f"class_{class_num}"
            for subject in primary_subjects:
                await self._create_subject(
                    db, subject, "cbse", class_level, "primary"
                )
        
        # Upper Primary Classes (6-8)
        upper_primary_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True},
            {"name": "Hindi", "code": "HIN", "category": "Language", "core": True},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": True},
            {"name": "Science", "code": "SCI", "category": "Science", "core": True},
            {"name": "Social Science", "code": "SST", "category": "Social_Science", "core": True},
            {"name": "Computer Science", "code": "CS", "category": "Technology", "core": False},
            {"name": "Sanskrit", "code": "SAN", "category": "Language", "core": False},
            {"name": "Art Education", "code": "ART", "category": "Arts", "core": False}
        ]
        
        for class_num in range(6, 9):
            class_level = f"class_{class_num}"
            for subject in upper_primary_subjects:
                await self._create_subject(
                    db, subject, "cbse", class_level, "upper_primary"
                )
        
        # Secondary Classes (9-10)
        secondary_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True},
            {"name": "Hindi", "code": "HIN", "category": "Language", "core": True},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": True},
            {"name": "Science", "code": "SCI", "category": "Science", "core": True},
            {"name": "Social Science", "code": "SST", "category": "Social_Science", "core": True},
            {"name": "Computer Science", "code": "CS", "category": "Technology", "core": False},
            {"name": "Sanskrit", "code": "SAN", "category": "Language", "core": False},
            {"name": "French", "code": "FRE", "category": "Language", "core": False},
            {"name": "Home Science", "code": "HS", "category": "Applied_Science", "core": False}
        ]
        
        for class_num in range(9, 11):
            class_level = f"class_{class_num}"
            for subject in secondary_subjects:
                await self._create_subject(
                    db, subject, "cbse", class_level, "secondary"
                )
        
        # Higher Secondary Classes (11-12)
        # Science Stream
        science_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True, "streams": ["science"]},
            {"name": "Physics", "code": "PHY", "category": "Science", "core": True, "streams": ["science"], "practical": True},
            {"name": "Chemistry", "code": "CHE", "category": "Science", "core": True, "streams": ["science"], "practical": True},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": True, "streams": ["science"]},
            {"name": "Biology", "code": "BIO", "category": "Science", "core": False, "streams": ["science"], "practical": True},
            {"name": "Computer Science", "code": "CS", "category": "Technology", "core": False, "streams": ["science"]},
            {"name": "Physical Education", "code": "PE", "category": "Physical", "core": False, "streams": ["science"]}
        ]
        
        # Commerce Stream
        commerce_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True, "streams": ["commerce"]},
            {"name": "Accountancy", "code": "ACC", "category": "Commerce", "core": True, "streams": ["commerce"]},
            {"name": "Business Studies", "code": "BS", "category": "Commerce", "core": True, "streams": ["commerce"]},
            {"name": "Economics", "code": "ECO", "category": "Commerce", "core": True, "streams": ["commerce"]},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": False, "streams": ["commerce"]},
            {"name": "Computer Science", "code": "CS", "category": "Technology", "core": False, "streams": ["commerce"]},
            {"name": "Entrepreneurship", "code": "ENT", "category": "Commerce", "core": False, "streams": ["commerce"]}
        ]
        
        # Arts/Humanities Stream
        arts_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True, "streams": ["arts"]},
            {"name": "History", "code": "HIS", "category": "Social_Science", "core": True, "streams": ["arts"]},
            {"name": "Political Science", "code": "PS", "category": "Social_Science", "core": True, "streams": ["arts"]},
            {"name": "Geography", "code": "GEO", "category": "Social_Science", "core": True, "streams": ["arts"]},
            {"name": "Psychology", "code": "PSY", "category": "Social_Science", "core": False, "streams": ["arts"]},
            {"name": "Economics", "code": "ECO", "category": "Social_Science", "core": False, "streams": ["arts"]},
            {"name": "Sociology", "code": "SOC", "category": "Social_Science", "core": False, "streams": ["arts"]}
        ]
        
        all_higher_secondary = science_subjects + commerce_subjects + arts_subjects
        
        for class_num in range(11, 13):
            class_level = f"class_{class_num}"
            for subject in all_higher_secondary:
                await self._create_subject(
                    db, subject, "cbse", class_level, "higher_secondary"
                )
    
    async def _create_icse_subjects(self, db: Session):
        """Create ICSE subjects for all classes"""
        
        # ICSE has similar structure but different emphasis
        # Primary Classes (1-5)
        primary_subjects = [
            {"name": "English", "code": "ENG", "category": "Language", "core": True},
            {"name": "Second Language", "code": "L2", "category": "Language", "core": True},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": True},
            {"name": "Environmental Science", "code": "EVS", "category": "Science", "core": True},
            {"name": "Art", "code": "ART", "category": "Arts", "core": False},
            {"name": "Music", "code": "MUS", "category": "Arts", "core": False}
        ]
        
        for class_num in range(1, 6):
            class_level = f"class_{class_num}"
            for subject in primary_subjects:
                await self._create_subject(
                    db, subject, "icse", class_level, "primary"
                )
        
        # Continue with other ICSE classes...
        # (Similar pattern for classes 6-12)
    
    async def _create_state_board_subjects(self, db: Session):
        """Create subjects for major state boards"""
        
        # Maharashtra State Board example
        maharashtra_subjects = [
            {"name": "Marathi", "code": "MAR", "category": "Language", "core": True},
            {"name": "English", "code": "ENG", "category": "Language", "core": True},
            {"name": "Hindi", "code": "HIN", "category": "Language", "core": False},
            {"name": "Mathematics", "code": "MAT", "category": "Mathematics", "core": True},
            {"name": "Science", "code": "SCI", "category": "Science", "core": True},
            {"name": "Social Studies", "code": "SS", "category": "Social_Science", "core": True}
        ]
        
        for class_num in range(1, 13):
            class_level = f"class_{class_num}"
            education_level = self._get_education_level(class_num)
            for subject in maharashtra_subjects:
                await self._create_subject(
                    db, subject, "maharashtra", class_level, education_level
                )
    
    async def _create_subject(
        self, 
        db: Session, 
        subject_data: Dict[str, Any], 
        board: str, 
        class_level: str, 
        education_level: str
    ):
        """Create a school subject"""
        
        # Check if subject already exists
        existing = db.query(SchoolSubject).filter(
            SchoolSubject.education_board == board,
            SchoolSubject.class_level == class_level,
            SchoolSubject.code == subject_data["code"]
        ).first()
        
        if existing:
            return existing
        
        subject = SchoolSubject(
            name=subject_data["name"],
            code=subject_data["code"],
            display_name=subject_data["name"],
            education_board=board,
            class_level=class_level,
            education_level=education_level,
            is_core_subject=subject_data.get("core", True),
            is_optional=not subject_data.get("core", True),
            is_language=subject_data.get("category") == "Language",
            subject_category=subject_data.get("category", "General"),
            applicable_streams=subject_data.get("streams", []),
            has_practical=subject_data.get("practical", False),
            theory_marks=80 if subject_data.get("practical") else 100,
            practical_marks=20 if subject_data.get("practical") else 0,
            internal_assessment_marks=20
        )
        
        db.add(subject)
        return subject
    
    def _get_education_level(self, class_num: int) -> str:
        """Get education level based on class number"""
        if class_num <= 5:
            return "primary"
        elif class_num <= 8:
            return "upper_primary"
        elif class_num <= 10:
            return "secondary"
        else:
            return "higher_secondary"
    
    async def get_subjects_by_class_and_board(
        self, 
        class_level: str, 
        education_board: str, 
        stream: Optional[str] = None,
        db: Session = None
    ) -> List[SchoolSubject]:
        """Get subjects for a specific class and board"""
        
        query = db.query(SchoolSubject).filter(
            SchoolSubject.class_level == class_level,
            SchoolSubject.education_board == education_board,
            SchoolSubject.is_active == True
        )
        
        if stream:
            query = query.filter(
                or_(
                    SchoolSubject.applicable_streams.is_(None),
                    SchoolSubject.applicable_streams.contains([stream])
                )
            )
        
        return query.order_by(
            SchoolSubject.is_core_subject.desc(),
            SchoolSubject.name
        ).all()
    
    async def create_academic_year(
        self,
        year_code: str,
        start_date: str,
        end_date: str,
        db: Session
    ) -> Tuple[bool, str, Optional[SchoolAcademicYear]]:
        """Create a new academic year"""
        
        try:
            from datetime import datetime
            
            # Check if academic year already exists
            existing = db.query(SchoolAcademicYear).filter(
                SchoolAcademicYear.year_code == year_code
            ).first()
            
            if existing:
                return False, "Academic year already exists", None
            
            academic_year = SchoolAcademicYear(
                year_code=year_code,
                name=f"Academic Year {year_code}",
                start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
                end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
                is_current=False,
                is_active=True
            )
            
            db.add(academic_year)
            db.commit()
            db.refresh(academic_year)
            
            return True, "Academic year created successfully", academic_year
            
        except Exception as e:
            db.rollback()
            return False, f"Error creating academic year: {str(e)}", None
    
    async def set_current_academic_year(
        self,
        year_code: str,
        db: Session
    ) -> Tuple[bool, str]:
        """Set the current academic year"""
        
        try:
            # Unset all current academic years
            db.query(SchoolAcademicYear).update({"is_current": False})
            
            # Set the specified year as current
            academic_year = db.query(SchoolAcademicYear).filter(
                SchoolAcademicYear.year_code == year_code
            ).first()
            
            if not academic_year:
                return False, "Academic year not found"
            
            academic_year.is_current = True
            db.commit()
            
            return True, f"Academic year {year_code} set as current"
            
        except Exception as e:
            db.rollback()
            return False, f"Error setting current academic year: {str(e)}"
    
    async def get_curriculum_for_class(
        self,
        education_board: str,
        class_level: str,
        stream: Optional[str] = None,
        academic_year: Optional[str] = None,
        db: Session = None
    ) -> Optional[SchoolCurriculum]:
        """Get curriculum for a specific class and board"""
        
        if not academic_year:
            academic_year = self.current_academic_year
        
        query = db.query(SchoolCurriculum).filter(
            SchoolCurriculum.education_board == education_board,
            SchoolCurriculum.class_level == class_level,
            SchoolCurriculum.academic_year == academic_year,
            SchoolCurriculum.is_current == True,
            SchoolCurriculum.is_active == True
        )
        
        if stream:
            query = query.filter(SchoolCurriculum.stream == stream)
        
        return query.first()
    
    async def get_education_statistics(self, db: Session) -> Dict[str, Any]:
        """Get comprehensive education system statistics"""
        
        # Count subjects by board
        subjects_by_board = db.query(
            SchoolSubject.education_board,
            func.count(SchoolSubject.id)
        ).filter(
            SchoolSubject.is_active == True
        ).group_by(SchoolSubject.education_board).all()
        
        # Count subjects by class level
        subjects_by_class = db.query(
            SchoolSubject.class_level,
            func.count(SchoolSubject.id)
        ).filter(
            SchoolSubject.is_active == True
        ).group_by(SchoolSubject.class_level).all()
        
        # Count curricula
        total_curricula = db.query(SchoolCurriculum).filter(
            SchoolCurriculum.is_active == True
        ).count()
        
        # Count academic years
        total_academic_years = db.query(SchoolAcademicYear).filter(
            SchoolAcademicYear.is_active == True
        ).count()
        
        return {
            "subjects_by_board": dict(subjects_by_board),
            "subjects_by_class": dict(subjects_by_class),
            "total_curricula": total_curricula,
            "total_academic_years": total_academic_years,
            "supported_boards": len(dict(subjects_by_board)),
            "supported_classes": len(dict(subjects_by_class))
        }


# Initialize global school education service
school_education_service = SchoolEducationService()
