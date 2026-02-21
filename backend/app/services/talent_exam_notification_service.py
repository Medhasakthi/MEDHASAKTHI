"""
Talent Exam Notification Service for MEDHASAKTHI
Handles automated notifications to institutes about talent exams
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.talent_exam import TalentExamNotification, TalentExam
from app.models.user import Institute, User
from app.services.email_service import email_service
from app.services.sms_service import sms_service
from app.services.push_notification_service import push_service
from app.core.database import get_db


class TalentExamNotificationService:
    """Service for managing talent exam notifications"""
    
    def __init__(self):
        self.notification_templates = self._load_notification_templates()
    
    def _load_notification_templates(self) -> Dict[str, Dict[str, str]]:
        """Load notification templates for different types"""
        return {
            'exam_scheduled': {
                'email_subject': '🎓 New Talent Exam Scheduled - {exam_title}',
                'email_template': 'talent_exam_scheduled.html',
                'sms_template': 'New talent exam "{exam_title}" scheduled for {class_level} on {exam_date}. Registration: {registration_start} to {registration_end}. Fee: ₹{fee}',
                'push_title': 'New Talent Exam',
                'push_body': '{exam_title} scheduled for {class_level} students'
            },
            'registration_open': {
                'email_subject': '📝 Registration Open - {exam_title}',
                'email_template': 'talent_exam_registration_open.html',
                'sms_template': 'Registration now open for "{exam_title}". Register your {class_level} students before {registration_end}.',
                'push_title': 'Registration Open',
                'push_body': 'Register now for {exam_title}'
            },
            'registration_reminder': {
                'email_subject': '⏰ Registration Opening Tomorrow - {exam_title}',
                'email_template': 'talent_exam_registration_reminder.html',
                'sms_template': 'Reminder: Registration for "{exam_title}" opens tomorrow. Prepare your {class_level} students!',
                'push_title': 'Registration Tomorrow',
                'push_body': '{exam_title} registration opens tomorrow'
            },
            'registration_closing': {
                'email_subject': '⚠️ Last Chance - Registration Closing Soon',
                'email_template': 'talent_exam_registration_closing.html',
                'sms_template': 'Last 3 days! Register your {class_level} students for "{exam_title}" before {registration_end}.',
                'push_title': 'Registration Closing',
                'push_body': 'Only 3 days left to register for {exam_title}'
            },
            'registration_closed': {
                'email_subject': '🔒 Registration Closed - {exam_title}',
                'email_template': 'talent_exam_registration_closed.html',
                'sms_template': 'Registration closed for "{exam_title}". Exam on {exam_date} at {exam_time}.',
                'push_title': 'Registration Closed',
                'push_body': '{exam_title} registration is now closed'
            },
            'exam_reminder': {
                'email_subject': '📅 Exam Tomorrow - {exam_title}',
                'email_template': 'talent_exam_reminder.html',
                'sms_template': 'Reminder: "{exam_title}" exam tomorrow at {exam_time}. Ensure students are prepared.',
                'push_title': 'Exam Tomorrow',
                'push_body': '{exam_title} exam is scheduled for tomorrow'
            },
            'date_change': {
                'email_subject': '🔄 Important: Exam Date Changed - {exam_title}',
                'email_template': 'talent_exam_date_change.html',
                'sms_template': 'IMPORTANT: "{exam_title}" exam date changed to {exam_date}. Please inform registered students.',
                'push_title': 'Exam Date Changed',
                'push_body': '{exam_title} rescheduled to {exam_date}'
            },
            'results_published': {
                'email_subject': '🏆 Results Published - {exam_title}',
                'email_template': 'talent_exam_results.html',
                'sms_template': 'Results for "{exam_title}" are now available. Check the portal for student performance.',
                'push_title': 'Results Available',
                'push_body': '{exam_title} results are now published'
            }
        }
    
    async def send_notification(self, notification: TalentExamNotification, db: Session) -> bool:
        """Send notification through configured channels"""
        
        try:
            # Get exam details
            exam = db.query(TalentExam).filter(TalentExam.id == notification.exam_id).first()
            if not exam:
                return False
            
            # Get target institutes
            target_institutes = await self._get_target_institutes(notification, db)
            
            if not target_institutes:
                return False
            
            # Prepare notification data
            notification_data = self._prepare_notification_data(exam, notification)
            
            # Send through different channels
            sent_count = 0
            
            if notification.send_email:
                email_sent = await self._send_email_notifications(
                    target_institutes, notification, notification_data
                )
                if email_sent:
                    sent_count += len(target_institutes)
            
            if notification.send_sms:
                sms_sent = await self._send_sms_notifications(
                    target_institutes, notification, notification_data
                )
                if sms_sent:
                    sent_count += len(target_institutes)
            
            if notification.send_push:
                push_sent = await self._send_push_notifications(
                    target_institutes, notification, notification_data
                )
                if push_sent:
                    sent_count += len(target_institutes)
            
            # Update notification status
            notification.status = 'sent'
            notification.sent_at = datetime.now()
            notification.recipients_count = len(target_institutes)
            notification.delivered_count = sent_count
            
            db.commit()
            
            return True
            
        except Exception as e:
            print(f"Error sending notification: {str(e)}")
            notification.status = 'failed'
            db.commit()
            return False
    
    async def _get_target_institutes(
        self, 
        notification: TalentExamNotification, 
        db: Session
    ) -> List[Institute]:
        """Get institutes that should receive the notification"""
        
        query = db.query(Institute).filter(Institute.is_active == True)
        
        # Filter by target states if specified
        if notification.target_states:
            query = query.filter(Institute.state.in_(notification.target_states))
        
        # Filter by specific institutes if specified
        if notification.target_institutes:
            query = query.filter(Institute.id.in_(notification.target_institutes))
        
        # Filter by institute type (schools for class-wise exams)
        if notification.target_class_levels:
            # Assuming schools have students in these class levels
            query = query.filter(Institute.institute_type.in_(['school', 'high_school', 'secondary_school']))
        
        return query.all()
    
    def _prepare_notification_data(
        self, 
        exam: TalentExam, 
        notification: TalentExamNotification
    ) -> Dict[str, Any]:
        """Prepare data for notification templates"""
        
        return {
            'exam_title': exam.title,
            'exam_code': exam.exam_code,
            'class_level': exam.class_level.replace('_', ' ').title(),
            'exam_date': exam.exam_date.strftime('%B %d, %Y'),
            'exam_time': exam.exam_time.strftime('%I:%M %p'),
            'registration_start': exam.registration_start_date.strftime('%B %d, %Y'),
            'registration_end': exam.registration_end_date.strftime('%B %d, %Y'),
            'fee': f"₹{exam.registration_fee}" if exam.registration_fee > 0 else "Free",
            'duration': f"{exam.duration_minutes} minutes",
            'total_questions': exam.total_questions,
            'total_marks': exam.total_marks,
            'academic_year': exam.academic_year,
            'exam_type': exam.exam_type.replace('_', ' ').title(),
            'notification_title': notification.title,
            'notification_message': notification.message
        }
    
    async def _send_email_notifications(
        self,
        institutes: List[Institute],
        notification: TalentExamNotification,
        data: Dict[str, Any]
    ) -> bool:
        """Send email notifications to institutes"""
        
        try:
            template_info = self.notification_templates.get(notification.notification_type, {})
            
            for institute in institutes:
                # Get institute admin emails
                admin_emails = self._get_institute_admin_emails(institute)
                
                for email in admin_emails:
                    await email_service.send_email(
                        to_email=email,
                        subject=template_info.get('email_subject', notification.title).format(**data),
                        template_name=template_info.get('email_template', 'default_notification.html'),
                        template_data={
                            **data,
                            'institute_name': institute.name,
                            'institute_code': institute.institute_code
                        }
                    )
            
            return True
            
        except Exception as e:
            print(f"Error sending email notifications: {str(e)}")
            return False
    
    async def _send_sms_notifications(
        self,
        institutes: List[Institute],
        notification: TalentExamNotification,
        data: Dict[str, Any]
    ) -> bool:
        """Send SMS notifications to institutes"""
        
        try:
            template_info = self.notification_templates.get(notification.notification_type, {})
            sms_message = template_info.get('sms_template', notification.message).format(**data)
            
            for institute in institutes:
                # Get institute admin phone numbers
                admin_phones = self._get_institute_admin_phones(institute)
                
                for phone in admin_phones:
                    await sms_service.send_sms(
                        phone_number=phone,
                        message=sms_message
                    )
            
            return True
            
        except Exception as e:
            print(f"Error sending SMS notifications: {str(e)}")
            return False
    
    async def _send_push_notifications(
        self,
        institutes: List[Institute],
        notification: TalentExamNotification,
        data: Dict[str, Any]
    ) -> bool:
        """Send push notifications to institutes"""
        
        try:
            template_info = self.notification_templates.get(notification.notification_type, {})
            
            push_title = template_info.get('push_title', notification.title).format(**data)
            push_body = template_info.get('push_body', notification.message).format(**data)
            
            for institute in institutes:
                # Get institute admin user tokens
                admin_tokens = self._get_institute_admin_tokens(institute)
                
                for token in admin_tokens:
                    await push_service.send_push_notification(
                        device_token=token,
                        title=push_title,
                        body=push_body,
                        data={
                            'type': 'talent_exam_notification',
                            'exam_id': str(notification.exam_id),
                            'notification_type': notification.notification_type
                        }
                    )
            
            return True
            
        except Exception as e:
            print(f"Error sending push notifications: {str(e)}")
            return False
    
    def _get_institute_admin_emails(self, institute: Institute) -> List[str]:
        """Get admin email addresses for an institute"""
        emails = []
        
        if institute.contact_email:
            emails.append(institute.contact_email)
        
        if institute.admin_email:
            emails.append(institute.admin_email)
        
        # Remove duplicates
        return list(set(emails))
    
    def _get_institute_admin_phones(self, institute: Institute) -> List[str]:
        """Get admin phone numbers for an institute"""
        phones = []
        
        if institute.contact_phone:
            phones.append(institute.contact_phone)
        
        if institute.admin_phone:
            phones.append(institute.admin_phone)
        
        # Remove duplicates and format
        return list(set(phones))
    
    def _get_institute_admin_tokens(self, institute: Institute) -> List[str]:
        """Get push notification tokens for institute admins"""
        # This would typically query user sessions or device tokens
        # For now, return empty list as this requires user session management
        return []
    
    async def process_scheduled_notifications(self, db: Session):
        """Process notifications that are scheduled to be sent"""
        
        try:
            # Get notifications scheduled for now or past
            scheduled_notifications = db.query(TalentExamNotification).filter(
                TalentExamNotification.status == 'scheduled',
                TalentExamNotification.scheduled_at <= datetime.now()
            ).all()
            
            for notification in scheduled_notifications:
                await self.send_notification(notification, db)
                
                # Small delay between notifications to avoid overwhelming
                await asyncio.sleep(1)
            
        except Exception as e:
            print(f"Error processing scheduled notifications: {str(e)}")
    
    async def send_bulk_notification(
        self,
        title: str,
        message: str,
        notification_type: str,
        target_class_levels: List[str],
        target_states: Optional[List[str]] = None,
        target_institutes: Optional[List[str]] = None,
        send_email: bool = True,
        send_sms: bool = False,
        send_push: bool = True,
        created_by: str = None,
        db: Session = None
    ) -> bool:
        """Send bulk notification to multiple institutes"""
        
        try:
            notification = TalentExamNotification(
                title=title,
                message=message,
                notification_type=notification_type,
                target_class_levels=target_class_levels,
                target_states=target_states,
                target_institutes=target_institutes,
                scheduled_at=datetime.now(),
                send_email=send_email,
                send_sms=send_sms,
                send_push=send_push,
                send_in_app=True,
                created_by=created_by,
                status='scheduled'
            )
            
            db.add(notification)
            db.commit()
            
            # Send immediately
            return await self.send_notification(notification, db)
            
        except Exception as e:
            print(f"Error sending bulk notification: {str(e)}")
            return False


# Initialize global notification service
talent_exam_notification_service = TalentExamNotificationService()
