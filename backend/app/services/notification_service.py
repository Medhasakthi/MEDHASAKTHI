"""
Comprehensive Notification Service for MEDHASAKTHI
Handles email, SMS, push notifications, and real-time alerts
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

import aioredis
from fastapi import WebSocket
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from twilio.rest import Client as TwilioClient
import firebase_admin
from firebase_admin import messaging

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification, NotificationPreference
from app.utils.templates import EmailTemplates

logger = logging.getLogger(__name__)

class NotificationService:
    """Comprehensive notification service with multiple channels"""
    
    def __init__(self):
        self.sendgrid_client = SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        self.twilio_client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        ) if settings.TWILIO_ACCOUNT_SID else None
        
        # Initialize Firebase for push notifications
        if settings.FIREBASE_CREDENTIALS:
            firebase_admin.initialize_app()
        
        # Redis for real-time notifications
        self.redis_client = None
        self.websocket_connections: Dict[str, List[WebSocket]] = {}
        self.email_templates = EmailTemplates()
    
    async def initialize_redis(self):
        """Initialize Redis connection for real-time notifications"""
        try:
            self.redis_client = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {str(e)}")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        content: str,
        template_id: Optional[str] = None,
        template_data: Optional[Dict] = None
    ) -> bool:
        """Send email notification"""
        try:
            from_email = Email(settings.FROM_EMAIL, settings.FROM_NAME)
            to_email_obj = To(to_email)
            
            if template_id and template_data:
                # Use SendGrid template
                mail = Mail(
                    from_email=from_email,
                    to_emails=to_email_obj,
                    subject=subject
                )
                mail.template_id = template_id
                mail.dynamic_template_data = template_data
            else:
                # Use plain content
                content_obj = Content("text/html", content)
                mail = Mail(from_email, to_email_obj, subject, content_obj)
            
            response = self.sendgrid_client.send(mail)
            
            if response.status_code in [200, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    async def send_sms(self, to_phone: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            if not self.twilio_client:
                logger.warning("Twilio client not configured")
                return False
            
            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to_phone
            )
            
            logger.info(f"SMS sent successfully to {to_phone}: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {str(e)}")
            return False
    
    async def send_push_notification(
        self,
        user_id: str,
        title: str,
        body: str,
        data: Optional[Dict] = None
    ) -> bool:
        """Send push notification via Firebase"""
        try:
            # Get user's FCM tokens from database
            # This would be stored when user registers for push notifications
            fcm_tokens = await self._get_user_fcm_tokens(user_id)
            
            if not fcm_tokens:
                logger.warning(f"No FCM tokens found for user {user_id}")
                return False
            
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data=data or {},
                tokens=fcm_tokens
            )
            
            response = messaging.send_multicast(message)
            
            logger.info(f"Push notification sent to {len(fcm_tokens)} devices")
            return response.success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
            return False
    
    async def send_real_time_notification(
        self,
        user_id: str,
        notification_type: str,
        data: Dict
    ) -> bool:
        """Send real-time notification via WebSocket"""
        try:
            if user_id in self.websocket_connections:
                message = {
                    "type": notification_type,
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                # Send to all active connections for this user
                connections = self.websocket_connections[user_id].copy()
                for websocket in connections:
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        # Remove dead connections
                        self.websocket_connections[user_id].remove(websocket)
                        logger.warning(f"Removed dead WebSocket connection: {str(e)}")
                
                return True
            else:
                # Store in Redis for when user comes online
                if self.redis_client:
                    await self.redis_client.lpush(
                        f"notifications:{user_id}",
                        json.dumps({
                            "type": notification_type,
                            "data": data,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    )
                    # Keep only last 100 notifications
                    await self.redis_client.ltrim(f"notifications:{user_id}", 0, 99)
                
                return False
                
        except Exception as e:
            logger.error(f"Error sending real-time notification: {str(e)}")
            return False
    
    async def register_websocket(self, user_id: str, websocket: WebSocket):
        """Register WebSocket connection for real-time notifications"""
        if user_id not in self.websocket_connections:
            self.websocket_connections[user_id] = []
        
        self.websocket_connections[user_id].append(websocket)
        
        # Send any pending notifications
        await self._send_pending_notifications(user_id, websocket)
    
    async def unregister_websocket(self, user_id: str, websocket: WebSocket):
        """Unregister WebSocket connection"""
        if user_id in self.websocket_connections:
            try:
                self.websocket_connections[user_id].remove(websocket)
                if not self.websocket_connections[user_id]:
                    del self.websocket_connections[user_id]
            except ValueError:
                pass
    
    async def send_exam_notification(
        self,
        user_id: str,
        exam_id: str,
        notification_type: str,
        data: Dict
    ):
        """Send exam-related notification"""
        try:
            # Get user preferences
            preferences = await self._get_user_preferences(user_id)
            
            # Prepare notification content
            if notification_type == "EXAM_STARTED":
                subject = "Exam Started"
                message = f"Your exam '{data.get('exam_title')}' has started."
                
            elif notification_type == "EXAM_SUBMITTED":
                subject = "Exam Submitted"
                message = f"Your exam '{data.get('exam_title')}' has been submitted successfully."
                
            elif notification_type == "EXAM_GRADED":
                subject = "Exam Results Available"
                message = f"Results for '{data.get('exam_title')}' are now available."
                
            elif notification_type == "EXAM_REMINDER":
                subject = "Exam Reminder"
                message = f"Reminder: Your exam '{data.get('exam_title')}' starts in {data.get('time_until')}."
                
            else:
                subject = "Exam Notification"
                message = data.get("message", "You have a new exam notification.")
            
            # Send via preferred channels
            await self._send_via_preferred_channels(
                user_id, subject, message, notification_type, data, preferences
            )
            
        except Exception as e:
            logger.error(f"Error sending exam notification: {str(e)}")
    
    async def send_proctor_alert(
        self,
        exam_id: str,
        student_id: str,
        violation_type: str,
        message: str,
        metadata: Dict
    ):
        """Send alert to proctors about exam violations"""
        try:
            # Get proctors for this exam
            proctors = await self._get_exam_proctors(exam_id)
            
            alert_data = {
                "exam_id": exam_id,
                "student_id": student_id,
                "violation_type": violation_type,
                "message": message,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Send real-time alerts to all proctors
            for proctor_id in proctors:
                await self.send_real_time_notification(
                    proctor_id,
                    "PROCTORING_ALERT",
                    alert_data
                )
                
                # Also send email for high-priority violations
                if violation_type in ["MULTIPLE_FACES", "EXAM_TERMINATED"]:
                    await self.send_email(
                        await self._get_user_email(proctor_id),
                        f"Urgent: Proctoring Alert - {violation_type}",
                        self.email_templates.proctor_alert_template(alert_data)
                    )
            
        except Exception as e:
            logger.error(f"Error sending proctor alert: {str(e)}")
    
    async def send_system_notification(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        notification_type: str = "SYSTEM",
        data: Optional[Dict] = None
    ):
        """Send system-wide notification to multiple users"""
        try:
            tasks = []
            
            for user_id in user_ids:
                # Real-time notification
                tasks.append(
                    self.send_real_time_notification(
                        user_id, notification_type, {
                            "title": title,
                            "message": message,
                            "data": data or {}
                        }
                    )
                )
                
                # Email notification
                tasks.append(
                    self.send_email(
                        await self._get_user_email(user_id),
                        title,
                        message
                    )
                )
            
            # Execute all notifications concurrently
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error sending system notification: {str(e)}")
    
    async def schedule_notification(
        self,
        user_id: str,
        notification_type: str,
        data: Dict,
        send_at: datetime
    ):
        """Schedule a notification to be sent at a specific time"""
        try:
            if self.redis_client:
                scheduled_notification = {
                    "user_id": user_id,
                    "notification_type": notification_type,
                    "data": data,
                    "send_at": send_at.isoformat()
                }
                
                # Store in Redis with expiration
                await self.redis_client.zadd(
                    "scheduled_notifications",
                    {json.dumps(scheduled_notification): send_at.timestamp()}
                )
                
                logger.info(f"Notification scheduled for {user_id} at {send_at}")
                
        except Exception as e:
            logger.error(f"Error scheduling notification: {str(e)}")
    
    async def process_scheduled_notifications(self):
        """Process and send scheduled notifications"""
        try:
            if not self.redis_client:
                return
            
            current_time = datetime.utcnow().timestamp()
            
            # Get notifications that should be sent now
            notifications = await self.redis_client.zrangebyscore(
                "scheduled_notifications",
                0,
                current_time,
                withscores=True
            )
            
            for notification_data, score in notifications:
                try:
                    notification = json.loads(notification_data)
                    
                    # Send the notification
                    await self.send_real_time_notification(
                        notification["user_id"],
                        notification["notification_type"],
                        notification["data"]
                    )
                    
                    # Remove from scheduled notifications
                    await self.redis_client.zrem("scheduled_notifications", notification_data)
                    
                except Exception as e:
                    logger.error(f"Error processing scheduled notification: {str(e)}")
                    
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {str(e)}")
    
    async def _send_via_preferred_channels(
        self,
        user_id: str,
        subject: str,
        message: str,
        notification_type: str,
        data: Dict,
        preferences: Dict
    ):
        """Send notification via user's preferred channels"""
        tasks = []
        
        # Real-time notification (always send)
        tasks.append(
            self.send_real_time_notification(user_id, notification_type, data)
        )
        
        # Email notification
        if preferences.get("email_enabled", True):
            tasks.append(
                self.send_email(
                    await self._get_user_email(user_id),
                    subject,
                    message
                )
            )
        
        # SMS notification
        if preferences.get("sms_enabled", False):
            phone = await self._get_user_phone(user_id)
            if phone:
                tasks.append(self.send_sms(phone, message))
        
        # Push notification
        if preferences.get("push_enabled", True):
            tasks.append(
                self.send_push_notification(user_id, subject, message, data)
            )
        
        # Execute all notifications concurrently
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_pending_notifications(self, user_id: str, websocket: WebSocket):
        """Send pending notifications when user comes online"""
        try:
            if self.redis_client:
                notifications = await self.redis_client.lrange(
                    f"notifications:{user_id}", 0, -1
                )
                
                for notification_data in notifications:
                    try:
                        await websocket.send_text(notification_data)
                    except Exception as e:
                        logger.warning(f"Failed to send pending notification: {str(e)}")
                        break
                
                # Clear sent notifications
                await self.redis_client.delete(f"notifications:{user_id}")
                
        except Exception as e:
            logger.error(f"Error sending pending notifications: {str(e)}")
    
    async def _get_user_preferences(self, user_id: str) -> Dict:
        """Get user notification preferences"""
        # This would query the database for user preferences
        # Placeholder implementation
        return {
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True
        }
    
    async def _get_user_email(self, user_id: str) -> str:
        """Get user email address"""
        # This would query the database for user email
        # Placeholder implementation
        return "user@example.com"
    
    async def _get_user_phone(self, user_id: str) -> Optional[str]:
        """Get user phone number"""
        # This would query the database for user phone
        # Placeholder implementation
        return None
    
    async def _get_user_fcm_tokens(self, user_id: str) -> List[str]:
        """Get user's FCM tokens for push notifications"""
        # This would query the database for user's FCM tokens
        # Placeholder implementation
        return []
    
    async def _get_exam_proctors(self, exam_id: str) -> List[str]:
        """Get list of proctor IDs for an exam"""
        # This would query the database for exam proctors
        # Placeholder implementation
        return []

# Global notification service instance
notification_service = NotificationService()
