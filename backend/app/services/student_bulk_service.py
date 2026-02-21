"""
Student Bulk Management Service for MEDHASAKTHI
Handles bulk student import, auto-credential generation, and institutional student management
"""
import csv
import io
import re
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from werkzeug.security import generate_password_hash
import pandas as pd

from app.models.user import User, Student, Institute
from app.core.security import get_password_hash
from app.services.email_service import email_service


class StudentBulkService:
    """Service for bulk student operations and institutional management"""
    
    def __init__(self):
        self.required_fields = [
            'student_id', 'first_name', 'last_name', 'class_level', 
            'section', 'academic_year', 'date_of_birth'
        ]
        self.optional_fields = [
            'roll_number', 'admission_number', 'education_board', 
            'medium_of_instruction', 'stream', 'father_name', 'mother_name',
            'guardian_phone', 'guardian_email', 'address', 'phone',
            'emergency_contact_name', 'emergency_contact_phone', 'gender',
            'blood_group', 'house', 'transport_required', 'hostel_required'
        ]
    
    def generate_student_credentials(self, student_id: str, institute_name: str) -> Tuple[str, str]:
        """Generate email and password for student"""
        
        # Clean institute name for email domain
        clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute_name.lower())
        
        # Generate email: studentid@institutename.com
        email = f"{student_id}@{clean_institute_name}.com"
        
        # Generate default password: institutename@123
        password = f"{clean_institute_name}@123"
        
        return email, password
    
    def validate_csv_data(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate CSV data for bulk import"""
        
        errors = []
        warnings = []
        valid_records = []
        
        # Check if required fields are present
        if not csv_data:
            return {
                "valid": False,
                "errors": ["CSV file is empty"],
                "warnings": [],
                "valid_records": [],
                "total_records": 0
            }
        
        # Check headers
        headers = set(csv_data[0].keys())
        missing_required = set(self.required_fields) - headers
        
        if missing_required:
            errors.append(f"Missing required fields: {', '.join(missing_required)}")
        
        # Validate each record
        for idx, record in enumerate(csv_data, 1):
            record_errors = []
            
            # Check required fields
            for field in self.required_fields:
                if not record.get(field) or str(record[field]).strip() == '':
                    record_errors.append(f"Row {idx}: Missing {field}")
            
            # Validate student_id format
            student_id = str(record.get('student_id', '')).strip()
            if student_id and not re.match(r'^[A-Za-z0-9_-]+$', student_id):
                record_errors.append(f"Row {idx}: Invalid student_id format. Use only letters, numbers, hyphens, and underscores")
            
            # Validate class_level
            class_level = str(record.get('class_level', '')).strip().lower()
            valid_classes = [f'class_{i}' for i in range(1, 13)] + ['nursery', 'lkg', 'ukg']
            if class_level and class_level not in valid_classes:
                record_errors.append(f"Row {idx}: Invalid class_level. Use format like 'class_1', 'class_2', etc.")
            
            # Validate email format if provided
            email = str(record.get('guardian_email', '')).strip()
            if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                record_errors.append(f"Row {idx}: Invalid guardian_email format")
            
            # Validate phone numbers
            for phone_field in ['phone', 'guardian_phone', 'emergency_contact_phone']:
                phone = str(record.get(phone_field, '')).strip()
                if phone and not re.match(r'^\+?[0-9\s\-\(\)]{10,15}$', phone):
                    warnings.append(f"Row {idx}: {phone_field} format may be invalid")
            
            if record_errors:
                errors.extend(record_errors)
            else:
                valid_records.append(record)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "valid_records": valid_records,
            "total_records": len(csv_data)
        }
    
    def process_csv_file(self, file_content: bytes, institute_id: str, db: Session) -> Dict[str, Any]:
        """Process CSV file and return validation results"""
        
        try:
            # Read CSV content
            csv_string = file_content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_string))
            csv_data = list(csv_reader)
            
            # Validate data
            validation_result = self.validate_csv_data(csv_data)
            
            if not validation_result["valid"]:
                return validation_result
            
            # Get institute details
            institute = db.query(Institute).filter(Institute.id == institute_id).first()
            if not institute:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Institute not found"
                )
            
            # Check for duplicate student IDs in database
            existing_student_ids = set()
            for record in validation_result["valid_records"]:
                student_id = record['student_id']
                existing = db.query(Student).filter(
                    and_(
                        Student.institute_id == institute_id,
                        Student.student_id == student_id
                    )
                ).first()
                
                if existing:
                    existing_student_ids.add(student_id)
            
            if existing_student_ids:
                validation_result["errors"].append(
                    f"Duplicate student IDs found in database: {', '.join(existing_student_ids)}"
                )
                validation_result["valid"] = False
            
            return validation_result
            
        except UnicodeDecodeError:
            return {
                "valid": False,
                "errors": ["Invalid file encoding. Please use UTF-8 encoded CSV file"],
                "warnings": [],
                "valid_records": [],
                "total_records": 0
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Error processing CSV file: {str(e)}"],
                "warnings": [],
                "valid_records": [],
                "total_records": 0
            }
    
    def bulk_import_students(
        self, 
        csv_data: List[Dict[str, Any]], 
        institute_id: str, 
        db: Session,
        send_credentials: bool = True
    ) -> Dict[str, Any]:
        """Bulk import students and create user accounts"""
        
        # Get institute details
        institute = db.query(Institute).filter(Institute.id == institute_id).first()
        if not institute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institute not found"
            )
        
        created_students = []
        failed_students = []
        credentials_list = []
        
        for record in csv_data:
            try:
                student_id = record['student_id']
                first_name = record['first_name']
                last_name = record['last_name']
                
                # Generate credentials
                email, default_password = self.generate_student_credentials(
                    student_id, institute.name
                )
                
                # Create User account
                user = User(
                    email=email,
                    full_name=f"{first_name} {last_name}",
                    password_hash=get_password_hash(default_password),
                    role="student",
                    is_active=True,
                    is_email_verified=True,  # Auto-verify for institutional accounts
                    institute_id=institute_id
                )
                
                db.add(user)
                db.flush()  # Get user ID
                
                # Create Student profile
                student = Student(
                    user_id=user.id,
                    institute_id=institute_id,
                    student_id=student_id,
                    roll_number=record.get('roll_number'),
                    class_level=record['class_level'],
                    section=record.get('section'),
                    academic_year=record['academic_year'],
                    admission_number=record.get('admission_number'),
                    education_board=record.get('education_board'),
                    medium_of_instruction=record.get('medium_of_instruction'),
                    stream=record.get('stream'),
                    auto_generated_email=email,
                    default_password_changed=False,
                    first_login_completed=False,
                    password_reset_required=True,
                    emergency_contact_name=record.get('emergency_contact_name'),
                    emergency_contact_phone=record.get('emergency_contact_phone')
                )
                
                # Add optional fields if provided
                if record.get('date_of_birth'):
                    try:
                        from datetime import datetime
                        student.enrollment_date = datetime.strptime(
                            record['date_of_birth'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass  # Skip invalid date format
                
                db.add(student)
                
                created_students.append({
                    'student_id': student_id,
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'class': record['class_level'],
                    'section': record.get('section', '')
                })
                
                credentials_list.append({
                    'student_id': student_id,
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'password': default_password,
                    'guardian_email': record.get('guardian_email')
                })
                
            except Exception as e:
                failed_students.append({
                    'student_id': record.get('student_id', 'Unknown'),
                    'name': f"{record.get('first_name', '')} {record.get('last_name', '')}",
                    'error': str(e)
                })
        
        # Commit all changes
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error during bulk import: {str(e)}"
            )
        
        # Send credentials via email if requested
        if send_credentials and credentials_list:
            self._send_bulk_credentials(credentials_list, institute.name)
        
        return {
            "success": True,
            "created_count": len(created_students),
            "failed_count": len(failed_students),
            "created_students": created_students,
            "failed_students": failed_students,
            "credentials": credentials_list if not send_credentials else []
        }
    
    def _send_bulk_credentials(self, credentials_list: List[Dict], institute_name: str):
        """Send login credentials to students/guardians via email"""
        
        for cred in credentials_list:
            try:
                # Send to guardian email if available, otherwise to student email
                recipient_email = cred.get('guardian_email') or cred['email']
                
                email_content = f"""
                Dear Parent/Guardian,

                Your ward {cred['name']} (Student ID: {cred['student_id']}) has been enrolled in the MEDHASAKTHI platform for {institute_name}.

                Login Credentials:
                Email: {cred['email']}
                Password: {cred['password']}

                Please note:
                1. The student must change the password on first login
                2. Keep these credentials secure
                3. Contact the institute for any issues

                Login at: https://medhasakthi.com/login

                Best regards,
                MEDHASAKTHI Team
                """
                
                email_service.send_email(
                    to_email=recipient_email,
                    subject=f"MEDHASAKTHI Login Credentials - {institute_name}",
                    content=email_content
                )
                
            except Exception as e:
                print(f"Failed to send credentials to {cred['student_id']}: {str(e)}")
    
    def generate_csv_template(self) -> str:
        """Generate CSV template for bulk import"""
        
        headers = self.required_fields + self.optional_fields
        
        # Create sample data
        sample_data = {
            'student_id': 'STU001',
            'first_name': 'John',
            'last_name': 'Doe',
            'class_level': 'class_10',
            'section': 'A',
            'academic_year': '2024-25',
            'date_of_birth': '2008-05-15',
            'roll_number': '001',
            'admission_number': 'ADM2024001',
            'education_board': 'CBSE',
            'medium_of_instruction': 'English',
            'stream': 'Science',
            'father_name': 'Robert Doe',
            'mother_name': 'Jane Doe',
            'guardian_phone': '+91-9876543210',
            'guardian_email': 'parent@example.com',
            'address': '123 Main Street, City, State - 123456',
            'phone': '+91-9876543211',
            'emergency_contact_name': 'Uncle John',
            'emergency_contact_phone': '+91-9876543212',
            'gender': 'Male',
            'blood_group': 'O+',
            'house': 'Red House',
            'transport_required': 'Yes',
            'hostel_required': 'No'
        }
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerow(sample_data)
        
        return output.getvalue()
    
    def get_student_credentials_report(self, institute_id: str, db: Session) -> List[Dict]:
        """Get report of all students with their login credentials"""
        
        students = db.query(Student).join(User).filter(
            Student.institute_id == institute_id,
            Student.is_active == True
        ).all()
        
        credentials_report = []
        for student in students:
            credentials_report.append({
                'student_id': student.student_id,
                'name': student.user.full_name,
                'email': student.auto_generated_email or student.user.email,
                'class': student.class_level,
                'section': student.section,
                'first_login_completed': student.first_login_completed,
                'password_changed': student.default_password_changed,
                'last_login': student.user.last_login_at.isoformat() if student.user.last_login_at else None
            })
        
        return credentials_report
    
    def reset_student_password(self, student_id: str, institute_id: str, db: Session) -> Dict[str, Any]:
        """Reset student password to default"""
        
        student = db.query(Student).join(User).filter(
            and_(
                Student.student_id == student_id,
                Student.institute_id == institute_id
            )
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Get institute name for password generation
        institute = db.query(Institute).filter(Institute.id == institute_id).first()
        clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute.name.lower())
        new_password = f"{clean_institute_name}@123"
        
        # Update password
        student.user.password_hash = get_password_hash(new_password)
        student.default_password_changed = False
        student.password_reset_required = True
        
        db.commit()
        
        return {
            "success": True,
            "student_id": student_id,
            "new_password": new_password,
            "message": "Password reset successfully"
        }


# Global instance
student_bulk_service = StudentBulkService()
