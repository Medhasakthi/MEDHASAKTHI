"""
Talent Exam Service for MEDHASAKTHI
Manages class-wise talent exams with centralized scheduling and notifications
"""
import uuid
import secrets
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from app.models.talent_exam import (
    TalentExam, TalentExamRegistration, ExamCenter, TalentExamSession,
    TalentExamNotification, ExamStatus, RegistrationStatus, ExamType, ClassLevel
)
from app.models.user import User, Institute, Student
from app.services.notification_service import notification_service
from app.services.email_service import email_service


class TalentExamService:
    """Service for managing talent exams"""
    
    def __init__(self):
        self.current_academic_year = self._get_current_academic_year()
    
    def _get_current_academic_year(self) -> str:
        """Get current academic year (e.g., 2024-25)"""
        now = datetime.now()
        if now.month >= 4:  # April onwards is new academic year
            return f"{now.year}-{str(now.year + 1)[2:]}"
        else:
            return f"{now.year - 1}-{str(now.year)[2:]}"
    
    def generate_exam_code(self, exam_type: str, class_level: str, academic_year: str) -> str:
        """Generate unique exam code"""
        type_prefix = exam_type.upper()[:3]
        class_num = class_level.split('_')[1] if '_' in class_level else class_level
        year_suffix = academic_year.split('-')[0][2:]
        random_suffix = secrets.token_hex(2).upper()
        
        return f"{type_prefix}{class_num}{year_suffix}{random_suffix}"
    
    def generate_registration_number(self, exam_code: str, sequence: int) -> str:
        """Generate registration number"""
        return f"REG{exam_code}{sequence:06d}"
    
    async def create_talent_exam(
        self,
        exam_data: Dict[str, Any],
        created_by: str,
        db: Session
    ) -> Tuple[bool, str, Optional[TalentExam]]:
        """Create a new talent exam"""
        
        try:
            # Generate exam code if not provided
            if 'exam_code' not in exam_data or not exam_data['exam_code']:
                exam_data['exam_code'] = self.generate_exam_code(
                    exam_data['exam_type'],
                    exam_data['class_level'],
                    exam_data['academic_year']
                )
            
            # Check if exam code already exists
            existing_exam = db.query(TalentExam).filter(
                TalentExam.exam_code == exam_data['exam_code']
            ).first()
            
            if existing_exam:
                return False, "Exam code already exists", None
            
            # Validate dates
            if exam_data['registration_end_date'] <= exam_data['registration_start_date']:
                return False, "Registration end date must be after start date", None
            
            if exam_data['exam_date'] <= exam_data['registration_end_date'].date():
                return False, "Exam date must be after registration end date", None
            
            # Create talent exam
            talent_exam = TalentExam(
                exam_code=exam_data['exam_code'],
                title=exam_data['title'],
                description=exam_data.get('description'),
                exam_type=exam_data['exam_type'],
                class_level=exam_data['class_level'],
                academic_year=exam_data['academic_year'],
                exam_date=exam_data['exam_date'],
                exam_time=exam_data['exam_time'],
                duration_minutes=exam_data['duration_minutes'],
                registration_start_date=exam_data['registration_start_date'],
                registration_end_date=exam_data['registration_end_date'],
                total_questions=exam_data['total_questions'],
                total_marks=exam_data['total_marks'],
                passing_marks=exam_data.get('passing_marks'),
                negative_marking=exam_data.get('negative_marking', False),
                negative_marks_per_question=exam_data.get('negative_marks_per_question', 0.0),
                subjects=exam_data.get('subjects', []),
                syllabus_details=exam_data.get('syllabus_details'),
                registration_fee=exam_data.get('registration_fee', 0.0),
                eligibility_criteria=exam_data.get('eligibility_criteria'),
                is_proctored=exam_data.get('is_proctored', True),
                allow_calculator=exam_data.get('allow_calculator', False),
                allow_rough_sheets=exam_data.get('allow_rough_sheets', True),
                randomize_questions=exam_data.get('randomize_questions', True),
                result_declaration_date=exam_data.get('result_declaration_date'),
                certificate_template_id=exam_data.get('certificate_template_id'),
                max_registrations=exam_data.get('max_registrations'),
                created_by=created_by,
                status=ExamStatus.SCHEDULED
            )
            
            db.add(talent_exam)
            db.commit()
            db.refresh(talent_exam)
            
            # Schedule automatic notifications
            await self._schedule_exam_notifications(talent_exam, db)
            
            return True, "Talent exam created successfully", talent_exam
            
        except Exception as e:
            db.rollback()
            return False, f"Error creating talent exam: {str(e)}", None
    
    async def update_exam_dates(
        self,
        exam_id: str,
        new_exam_date: date,
        new_exam_time: Optional[Any] = None,
        new_registration_start: Optional[datetime] = None,
        new_registration_end: Optional[datetime] = None,
        updated_by: str = None,
        db: Session = None
    ) -> Tuple[bool, str]:
        """Update exam dates and notify institutes"""
        
        try:
            exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
            if not exam:
                return False, "Exam not found"
            
            old_exam_date = exam.exam_date
            old_registration_end = exam.registration_end_date
            
            # Update dates
            exam.exam_date = new_exam_date
            if new_exam_time:
                exam.exam_time = new_exam_time
            if new_registration_start:
                exam.registration_start_date = new_registration_start
            if new_registration_end:
                exam.registration_end_date = new_registration_end
            
            exam.updated_at = datetime.now()
            
            db.commit()
            
            # Send notifications about date change
            await self._notify_date_change(exam, old_exam_date, old_registration_end, db)
            
            return True, "Exam dates updated successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error updating exam dates: {str(e)}"
    
    async def open_registration(self, exam_id: str, db: Session) -> Tuple[bool, str]:
        """Open registration for an exam"""
        
        try:
            exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
            if not exam:
                return False, "Exam not found"
            
            if exam.status != ExamStatus.SCHEDULED:
                return False, f"Cannot open registration for exam in {exam.status} status"
            
            # Check if registration period is valid
            now = datetime.now()
            if now < exam.registration_start_date:
                return False, "Registration start date has not arrived yet"
            
            if now > exam.registration_end_date:
                return False, "Registration period has already ended"
            
            # Update status
            exam.status = ExamStatus.REGISTRATION_OPEN
            exam.updated_at = now
            
            db.commit()
            
            # Send registration open notifications
            await self._notify_registration_open(exam, db)
            
            return True, "Registration opened successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error opening registration: {str(e)}"
    
    async def close_registration(self, exam_id: str, db: Session) -> Tuple[bool, str]:
        """Close registration for an exam"""
        
        try:
            exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
            if not exam:
                return False, "Exam not found"
            
            if exam.status != ExamStatus.REGISTRATION_OPEN:
                return False, f"Cannot close registration for exam in {exam.status} status"
            
            # Update status
            exam.status = ExamStatus.REGISTRATION_CLOSED
            exam.updated_at = datetime.now()
            
            db.commit()
            
            # Send registration closed notifications
            await self._notify_registration_closed(exam, db)
            
            return True, "Registration closed successfully"
            
        except Exception as e:
            db.rollback()
            return False, f"Error closing registration: {str(e)}"
    
    async def get_exam_statistics(self, exam_id: str, db: Session) -> Dict[str, Any]:
        """Get comprehensive exam statistics"""
        
        exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
        if not exam:
            return {}
        
        # Registration statistics
        total_registrations = db.query(TalentExamRegistration).filter(
            TalentExamRegistration.exam_id == exam_id
        ).count()
        
        registrations_by_status = db.query(
            TalentExamRegistration.status,
            func.count(TalentExamRegistration.id)
        ).filter(
            TalentExamRegistration.exam_id == exam_id
        ).group_by(TalentExamRegistration.status).all()
        
        # State-wise registrations
        registrations_by_state = db.query(
            func.json_extract_path_text(TalentExamRegistration.address, 'state').label('state'),
            func.count(TalentExamRegistration.id)
        ).filter(
            TalentExamRegistration.exam_id == exam_id
        ).group_by('state').all()
        
        # Institute-wise registrations
        registrations_by_institute = db.query(
            TalentExamRegistration.institute_id,
            func.count(TalentExamRegistration.id)
        ).filter(
            TalentExamRegistration.exam_id == exam_id
        ).group_by(TalentExamRegistration.institute_id).all()
        
        # Payment statistics
        total_fee_collected = db.query(
            func.sum(TalentExamRegistration.registration_fee_paid)
        ).filter(
            TalentExamRegistration.exam_id == exam_id,
            TalentExamRegistration.payment_status == 'completed'
        ).scalar() or 0
        
        return {
            'exam_details': {
                'id': exam.id,
                'title': exam.title,
                'exam_code': exam.exam_code,
                'class_level': exam.class_level,
                'exam_date': exam.exam_date.isoformat(),
                'status': exam.status
            },
            'registration_stats': {
                'total_registrations': total_registrations,
                'max_registrations': exam.max_registrations,
                'registrations_by_status': dict(registrations_by_status),
                'registrations_by_state': dict(registrations_by_state),
                'registrations_by_institute': dict(registrations_by_institute)
            },
            'financial_stats': {
                'total_fee_collected': float(total_fee_collected),
                'expected_revenue': exam.registration_fee * total_registrations if exam.registration_fee else 0
            },
            'timeline': {
                'registration_start': exam.registration_start_date.isoformat(),
                'registration_end': exam.registration_end_date.isoformat(),
                'exam_date': exam.exam_date.isoformat(),
                'result_declaration': exam.result_declaration_date.isoformat() if exam.result_declaration_date else None
            }
        }
    
    async def get_upcoming_exams(self, class_level: Optional[str] = None, db: Session = None) -> List[Dict[str, Any]]:
        """Get upcoming exams for notification scheduling"""
        
        query = db.query(TalentExam).filter(
            TalentExam.exam_date >= date.today(),
            TalentExam.is_active == True
        )
        
        if class_level:
            query = query.filter(TalentExam.class_level == class_level)
        
        exams = query.order_by(TalentExam.exam_date).all()
        
        return [
            {
                'id': str(exam.id),
                'title': exam.title,
                'exam_code': exam.exam_code,
                'class_level': exam.class_level,
                'exam_date': exam.exam_date.isoformat(),
                'exam_time': exam.exam_time.isoformat(),
                'registration_start': exam.registration_start_date.isoformat(),
                'registration_end': exam.registration_end_date.isoformat(),
                'status': exam.status,
                'registration_fee': exam.registration_fee
            }
            for exam in exams
        ]
    
    async def _schedule_exam_notifications(self, exam: TalentExam, db: Session):
        """Schedule automatic notifications for exam milestones"""
        
        notifications = [
            {
                'title': f'New Talent Exam Scheduled - {exam.title}',
                'message': f'A new talent exam "{exam.title}" has been scheduled for {exam.class_level.replace("_", " ").title()} students on {exam.exam_date.strftime("%B %d, %Y")}. Registration opens on {exam.registration_start_date.strftime("%B %d, %Y")}.',
                'notification_type': 'exam_scheduled',
                'scheduled_at': datetime.now() + timedelta(minutes=5),  # Send immediately
                'target_class_levels': [exam.class_level]
            },
            {
                'title': f'Registration Opening Soon - {exam.title}',
                'message': f'Registration for "{exam.title}" opens tomorrow. Don\'t miss this opportunity for your {exam.class_level.replace("_", " ").title()} students!',
                'notification_type': 'registration_reminder',
                'scheduled_at': exam.registration_start_date - timedelta(days=1),
                'target_class_levels': [exam.class_level]
            },
            {
                'title': f'Registration Closing Soon - {exam.title}',
                'message': f'Last chance! Registration for "{exam.title}" closes in 3 days. Register your students now.',
                'notification_type': 'registration_closing',
                'scheduled_at': exam.registration_end_date - timedelta(days=3),
                'target_class_levels': [exam.class_level]
            },
            {
                'title': f'Exam Tomorrow - {exam.title}',
                'message': f'Reminder: "{exam.title}" exam is scheduled for tomorrow at {exam.exam_time.strftime("%I:%M %p")}. Ensure all registered students are prepared.',
                'notification_type': 'exam_reminder',
                'scheduled_at': datetime.combine(exam.exam_date, exam.exam_time) - timedelta(days=1),
                'target_class_levels': [exam.class_level]
            }
        ]
        
        for notification_data in notifications:
            # Only schedule future notifications
            if notification_data['scheduled_at'] > datetime.now():
                notification = TalentExamNotification(
                    title=notification_data['title'],
                    message=notification_data['message'],
                    notification_type=notification_data['notification_type'],
                    exam_id=exam.id,
                    target_class_levels=notification_data['target_class_levels'],
                    scheduled_at=notification_data['scheduled_at'],
                    created_by=exam.created_by,
                    status='scheduled'
                )
                
                db.add(notification)
        
        db.commit()
    
    async def _notify_date_change(
        self, 
        exam: TalentExam, 
        old_date: date, 
        old_registration_end: datetime, 
        db: Session
    ):
        """Notify institutes about exam date changes"""
        
        notification = TalentExamNotification(
            title=f'Important: Exam Date Changed - {exam.title}',
            message=f'The exam date for "{exam.title}" has been changed from {old_date.strftime("%B %d, %Y")} to {exam.exam_date.strftime("%B %d, %Y")}. Please inform your registered students.',
            notification_type='date_change',
            exam_id=exam.id,
            target_class_levels=[exam.class_level],
            scheduled_at=datetime.now(),
            created_by=exam.created_by,
            status='scheduled'
        )
        
        db.add(notification)
        db.commit()
        
        # Send immediate notification
        await notification_service.send_notification(notification, db)
    
    async def _notify_registration_open(self, exam: TalentExam, db: Session):
        """Notify institutes that registration is open"""
        
        notification = TalentExamNotification(
            title=f'Registration Now Open - {exam.title}',
            message=f'Registration is now open for "{exam.title}" scheduled on {exam.exam_date.strftime("%B %d, %Y")}. Register your {exam.class_level.replace("_", " ").title()} students before {exam.registration_end_date.strftime("%B %d, %Y")}.',
            notification_type='registration_open',
            exam_id=exam.id,
            target_class_levels=[exam.class_level],
            scheduled_at=datetime.now(),
            created_by=exam.created_by,
            status='scheduled'
        )
        
        db.add(notification)
        db.commit()
        
        # Send immediate notification
        await notification_service.send_notification(notification, db)
    
    async def _notify_registration_closed(self, exam: TalentExam, db: Session):
        """Notify institutes that registration is closed"""
        
        notification = TalentExamNotification(
            title=f'Registration Closed - {exam.title}',
            message=f'Registration for "{exam.title}" is now closed. Exam will be conducted on {exam.exam_date.strftime("%B %d, %Y")} at {exam.exam_time.strftime("%I:%M %p")}.',
            notification_type='registration_closed',
            exam_id=exam.id,
            target_class_levels=[exam.class_level],
            scheduled_at=datetime.now(),
            created_by=exam.created_by,
            status='scheduled'
        )
        
        db.add(notification)
        db.commit()
        
        # Send immediate notification
        await notification_service.send_notification(notification, db)


# Initialize global talent exam service
talent_exam_service = TalentExamService()
