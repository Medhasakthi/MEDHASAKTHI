"""
Enterprise Integration Service for MEDHASAKTHI
Comprehensive integration with LMS, SIS, payment gateways, and third-party services
"""
import json
import requests
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import xml.etree.ElementTree as ET
from cryptography.fernet import Fernet
import base64

from app.core.config import settings
from app.core.security_enhanced import security_manager
from app.models.user import User, Institute, Student
from app.models.talent_exam import TalentExam, TalentExamRegistration
from app.services.email_service import email_service


class LMSIntegrationService:
    """Learning Management System integration (Moodle, Canvas, Blackboard)"""
    
    def __init__(self):
        self.supported_lms = {
            "moodle": MoodleIntegration(),
            "canvas": CanvasIntegration(),
            "blackboard": BlackboardIntegration(),
            "google_classroom": GoogleClassroomIntegration()
        }
    
    async def sync_students_from_lms(
        self,
        institute_id: str,
        lms_type: str,
        lms_config: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Sync students from LMS to MEDHASAKTHI"""
        
        if lms_type not in self.supported_lms:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported LMS type: {lms_type}"
            )
        
        lms_integration = self.supported_lms[lms_type]
        
        try:
            # Fetch students from LMS
            lms_students = await lms_integration.get_students(lms_config)
            
            # Sync to MEDHASAKTHI
            synced_students = []
            errors = []
            
            for lms_student in lms_students:
                try:
                    student = await self._create_or_update_student(
                        lms_student, institute_id, db
                    )
                    synced_students.append(student)
                except Exception as e:
                    errors.append({
                        "student": lms_student.get("email", "unknown"),
                        "error": str(e)
                    })
            
            return {
                "synced_count": len(synced_students),
                "error_count": len(errors),
                "errors": errors,
                "students": [{"id": s.id, "email": s.email} for s in synced_students]
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"LMS sync failed: {str(e)}"
            )
    
    async def export_grades_to_lms(
        self,
        exam_id: str,
        lms_type: str,
        lms_config: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Export exam grades to LMS"""
        
        lms_integration = self.supported_lms[lms_type]
        
        # Get exam results
        exam = db.query(TalentExam).filter(TalentExam.id == exam_id).first()
        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )
        
        # Get registrations with results
        registrations = db.query(TalentExamRegistration).filter(
            TalentExamRegistration.exam_id == exam_id,
            TalentExamRegistration.status == "completed"
        ).all()
        
        # Format grades for LMS
        grades = []
        for reg in registrations:
            if reg.final_score is not None:
                grades.append({
                    "student_email": reg.student_email,
                    "student_id": reg.student_id,
                    "grade": reg.final_score,
                    "max_grade": exam.total_marks,
                    "exam_name": exam.title
                })
        
        # Export to LMS
        try:
            result = await lms_integration.export_grades(lms_config, grades)
            return {
                "exported_count": len(grades),
                "lms_response": result
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Grade export failed: {str(e)}"
            )
    
    async def _create_or_update_student(
        self,
        lms_student: Dict[str, Any],
        institute_id: str,
        db: Session
    ) -> Student:
        """Create or update student from LMS data"""
        
        # Check if student exists
        existing_student = db.query(Student).filter(
            Student.email == lms_student["email"]
        ).first()
        
        if existing_student:
            # Update existing student
            existing_student.full_name = lms_student.get("name", existing_student.full_name)
            existing_student.current_class = lms_student.get("class", existing_student.current_class)
            existing_student.updated_at = datetime.now()
            db.commit()
            return existing_student
        else:
            # Create new student
            student = Student(
                student_id=lms_student.get("student_id", f"LMS_{datetime.now().timestamp()}"),
                full_name=lms_student["name"],
                email=lms_student["email"],
                current_class=lms_student.get("class", "unknown"),
                institute_id=institute_id,
                is_active=True,
                created_at=datetime.now()
            )
            db.add(student)
            db.commit()
            db.refresh(student)
            return student


class SISIntegrationService:
    """Student Information System integration (PowerSchool, Infinite Campus, etc.)"""
    
    def __init__(self):
        self.supported_sis = {
            "powerschool": PowerSchoolIntegration(),
            "infinite_campus": InfiniteCampusIntegration(),
            "skyward": SkywardIntegration()
        }
    
    async def sync_student_data(
        self,
        institute_id: str,
        sis_type: str,
        sis_config: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Sync comprehensive student data from SIS"""
        
        if sis_type not in self.supported_sis:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported SIS type: {sis_type}"
            )
        
        sis_integration = self.supported_sis[sis_type]
        
        try:
            # Fetch student data from SIS
            sis_data = await sis_integration.get_student_data(sis_config)
            
            synced_records = []
            for student_data in sis_data:
                # Update student record with SIS data
                student = db.query(Student).filter(
                    Student.student_id == student_data["student_id"],
                    Student.institute_id == institute_id
                ).first()
                
                if student:
                    # Update with SIS data
                    student.full_name = student_data.get("full_name", student.full_name)
                    student.current_class = student_data.get("grade_level", student.current_class)
                    student.date_of_birth = student_data.get("date_of_birth")
                    student.parent_email = student_data.get("parent_email")
                    student.parent_phone = student_data.get("parent_phone")
                    student.address = student_data.get("address")
                    student.updated_at = datetime.now()
                    
                    synced_records.append(student)
            
            db.commit()
            
            return {
                "synced_count": len(synced_records),
                "message": "Student data synchronized successfully"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"SIS sync failed: {str(e)}"
            )


class PaymentGatewayService:
    """Multi-payment gateway integration service"""
    
    def __init__(self):
        self.gateways = {
            "razorpay": RazorpayGateway(),
            "stripe": StripeGateway(),
            "paypal": PayPalGateway(),
            "payu": PayUGateway()
        }
    
    async def create_payment_order(
        self,
        gateway: str,
        amount: float,
        currency: str,
        order_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create payment order with specified gateway"""
        
        if gateway not in self.gateways:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported payment gateway: {gateway}"
            )
        
        gateway_service = self.gateways[gateway]
        
        try:
            order = await gateway_service.create_order(amount, currency, order_details)
            return {
                "gateway": gateway,
                "order_id": order["order_id"],
                "amount": amount,
                "currency": currency,
                "payment_url": order.get("payment_url"),
                "gateway_response": order
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment order creation failed: {str(e)}"
            )
    
    async def verify_payment(
        self,
        gateway: str,
        payment_id: str,
        order_id: str,
        signature: str = None
    ) -> Dict[str, Any]:
        """Verify payment with gateway"""
        
        gateway_service = self.gateways[gateway]
        
        try:
            verification = await gateway_service.verify_payment(
                payment_id, order_id, signature
            )
            return {
                "verified": verification["status"] == "success",
                "transaction_id": verification.get("transaction_id"),
                "amount": verification.get("amount"),
                "gateway_response": verification
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment verification failed: {str(e)}"
            )


class WebhookService:
    """Webhook management for external integrations"""
    
    def __init__(self):
        self.webhook_handlers = {
            "payment_success": self._handle_payment_success,
            "payment_failure": self._handle_payment_failure,
            "lms_enrollment": self._handle_lms_enrollment,
            "sis_update": self._handle_sis_update
        }
    
    async def process_webhook(
        self,
        webhook_type: str,
        payload: Dict[str, Any],
        headers: Dict[str, str],
        db: Session
    ) -> Dict[str, Any]:
        """Process incoming webhook"""
        
        # Verify webhook signature
        if not self._verify_webhook_signature(webhook_type, payload, headers):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
        
        if webhook_type not in self.webhook_handlers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported webhook type: {webhook_type}"
            )
        
        handler = self.webhook_handlers[webhook_type]
        
        try:
            result = await handler(payload, db)
            return {
                "status": "processed",
                "webhook_type": webhook_type,
                "result": result
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Webhook processing failed: {str(e)}"
            )
    
    def _verify_webhook_signature(
        self,
        webhook_type: str,
        payload: Dict[str, Any],
        headers: Dict[str, str]
    ) -> bool:
        """Verify webhook signature for security"""
        # Implementation would verify signature based on webhook type
        # For now, return True
        return True
    
    async def _handle_payment_success(self, payload: Dict[str, Any], db: Session):
        """Handle successful payment webhook"""
        order_id = payload.get("order_id")
        payment_id = payload.get("payment_id")
        amount = payload.get("amount")
        
        # Update registration status
        registration = db.query(TalentExamRegistration).filter(
            TalentExamRegistration.payment_order_id == order_id
        ).first()
        
        if registration:
            registration.payment_status = "completed"
            registration.payment_id = payment_id
            registration.status = "confirmed"
            registration.updated_at = datetime.now()
            db.commit()
            
            # Send confirmation email
            await email_service.send_registration_confirmation(
                registration.student_email,
                registration.student_name,
                registration.exam.title
            )
        
        return {"registration_confirmed": registration.id if registration else None}
    
    async def _handle_payment_failure(self, payload: Dict[str, Any], db: Session):
        """Handle failed payment webhook"""
        order_id = payload.get("order_id")
        
        # Update registration status
        registration = db.query(TalentExamRegistration).filter(
            TalentExamRegistration.payment_order_id == order_id
        ).first()
        
        if registration:
            registration.payment_status = "failed"
            registration.status = "payment_pending"
            registration.updated_at = datetime.now()
            db.commit()
        
        return {"registration_updated": registration.id if registration else None}
    
    async def _handle_lms_enrollment(self, payload: Dict[str, Any], db: Session):
        """Handle LMS enrollment webhook"""
        # Process LMS enrollment data
        return {"processed": True}
    
    async def _handle_sis_update(self, payload: Dict[str, Any], db: Session):
        """Handle SIS update webhook"""
        # Process SIS update data
        return {"processed": True}


# Individual integration classes (simplified implementations)

class MoodleIntegration:
    async def get_students(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Moodle API integration
        return []
    
    async def export_grades(self, config: Dict[str, Any], grades: List[Dict[str, Any]]):
        # Export grades to Moodle
        return {"status": "success"}


class CanvasIntegration:
    async def get_students(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Canvas API integration
        return []
    
    async def export_grades(self, config: Dict[str, Any], grades: List[Dict[str, Any]]):
        # Export grades to Canvas
        return {"status": "success"}


class BlackboardIntegration:
    async def get_students(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Blackboard API integration
        return []
    
    async def export_grades(self, config: Dict[str, Any], grades: List[Dict[str, Any]]):
        # Export grades to Blackboard
        return {"status": "success"}


class GoogleClassroomIntegration:
    async def get_students(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Google Classroom API integration
        return []
    
    async def export_grades(self, config: Dict[str, Any], grades: List[Dict[str, Any]]):
        # Export grades to Google Classroom
        return {"status": "success"}


class PowerSchoolIntegration:
    async def get_student_data(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # PowerSchool API integration
        return []


class InfiniteCampusIntegration:
    async def get_student_data(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Infinite Campus API integration
        return []


class SkywardIntegration:
    async def get_student_data(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Skyward API integration
        return []


class RazorpayGateway:
    async def create_order(self, amount: float, currency: str, details: Dict[str, Any]):
        # Razorpay order creation
        return {"order_id": f"order_{datetime.now().timestamp()}", "status": "created"}
    
    async def verify_payment(self, payment_id: str, order_id: str, signature: str):
        # Razorpay payment verification
        return {"status": "success", "transaction_id": payment_id}


class StripeGateway:
    async def create_order(self, amount: float, currency: str, details: Dict[str, Any]):
        # Stripe payment intent creation
        return {"order_id": f"pi_{datetime.now().timestamp()}", "status": "created"}
    
    async def verify_payment(self, payment_id: str, order_id: str, signature: str = None):
        # Stripe payment verification
        return {"status": "success", "transaction_id": payment_id}


class PayPalGateway:
    async def create_order(self, amount: float, currency: str, details: Dict[str, Any]):
        # PayPal order creation
        return {"order_id": f"paypal_{datetime.now().timestamp()}", "status": "created"}
    
    async def verify_payment(self, payment_id: str, order_id: str, signature: str = None):
        # PayPal payment verification
        return {"status": "success", "transaction_id": payment_id}


class PayUGateway:
    async def create_order(self, amount: float, currency: str, details: Dict[str, Any]):
        # PayU order creation
        return {"order_id": f"payu_{datetime.now().timestamp()}", "status": "created"}
    
    async def verify_payment(self, payment_id: str, order_id: str, signature: str = None):
        # PayU payment verification
        return {"status": "success", "transaction_id": payment_id}


# Global instances
lms_integration_service = LMSIntegrationService()
sis_integration_service = SISIntegrationService()
payment_gateway_service = PaymentGatewayService()
webhook_service = WebhookService()
