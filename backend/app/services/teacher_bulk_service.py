"""
Teacher Bulk Management Service for MEDHASAKTHI
Handles bulk teacher import, credential generation, and teacher-specific operations
"""
import csv
import io
import re
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status

from app.models.user import User, Teacher, Institute
from app.core.security import get_password_hash
from app.services.email_service import email_service


class TeacherBulkService:
    """Service for bulk teacher operations and institutional management"""
    
    def __init__(self):
        self.required_fields = [
            'teacher_id', 'first_name', 'last_name', 'subject_specialization',
            'qualification', 'experience_years', 'phone', 'email'
        ]
        self.optional_fields = [
            'employee_id', 'department', 'designation', 'joining_date',
            'salary_grade', 'address', 'emergency_contact_name', 
            'emergency_contact_phone', 'date_of_birth', 'gender',
            'blood_group', 'aadhar_number', 'pan_number', 'classes_assigned',
            'subjects_assigned', 'is_class_teacher', 'class_teacher_of'
        ]
    
    def generate_teacher_credentials(self, teacher_id: str, institute_name: str) -> Tuple[str, str]:
        """Generate email and password for teacher"""
        
        # Clean institute name for email domain
        clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute_name.lower())
        
        # Generate email: teacherid@institutename.com
        email = f"{teacher_id}@{clean_institute_name}.com"
        
        # Generate default password: institutename@123
        password = f"{clean_institute_name}@123"
        
        return email, password
    
    def validate_csv_data(self, csv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate CSV data for bulk teacher import"""
        
        errors = []
        warnings = []
        valid_records = []
        
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
            
            # Validate teacher_id format
            teacher_id = str(record.get('teacher_id', '')).strip()
            if teacher_id and not re.match(r'^[A-Za-z0-9_-]+$', teacher_id):
                record_errors.append(f"Row {idx}: Invalid teacher_id format")
            
            # Validate email format
            email = str(record.get('email', '')).strip()
            if email and not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
                record_errors.append(f"Row {idx}: Invalid email format")
            
            # Validate phone number
            phone = str(record.get('phone', '')).strip()
            if phone and not re.match(r'^\+?[0-9\s\-\(\)]{10,15}$', phone):
                warnings.append(f"Row {idx}: Phone number format may be invalid")
            
            # Validate experience years
            try:
                exp_years = int(record.get('experience_years', 0))
                if exp_years < 0 or exp_years > 50:
                    warnings.append(f"Row {idx}: Experience years seems unusual")
            except ValueError:
                record_errors.append(f"Row {idx}: Experience years must be a number")
            
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
    
    def bulk_import_teachers(
        self, 
        csv_data: List[Dict[str, Any]], 
        institute_id: str, 
        db: Session,
        send_credentials: bool = True
    ) -> Dict[str, Any]:
        """Bulk import teachers and create user accounts"""
        
        # Get institute details
        institute = db.query(Institute).filter(Institute.id == institute_id).first()
        if not institute:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institute not found"
            )
        
        created_teachers = []
        failed_teachers = []
        credentials_list = []
        
        for record in csv_data:
            try:
                teacher_id = record['teacher_id']
                first_name = record['first_name']
                last_name = record['last_name']
                
                # Use provided email or generate credentials
                if record.get('email') and '@' in record['email']:
                    email = record['email']
                    password = f"{institute.name.lower().replace(' ', '')}@123"
                    auto_generated = False
                else:
                    email, password = self.generate_teacher_credentials(
                        teacher_id, institute.name
                    )
                    auto_generated = True
                
                # Create User account
                user = User(
                    email=email,
                    full_name=f"{first_name} {last_name}",
                    password_hash=get_password_hash(password),
                    role="teacher",
                    is_active=True,
                    is_email_verified=True,  # Auto-verify for institutional accounts
                    institute_id=institute_id
                )
                
                db.add(user)
                db.flush()  # Get user ID
                
                # Create Teacher profile
                teacher = Teacher(
                    user_id=user.id,
                    institute_id=institute_id,
                    teacher_id=teacher_id,
                    employee_id=record.get('employee_id'),
                    subject_specialization=record['subject_specialization'],
                    qualification=record['qualification'],
                    experience_years=int(record.get('experience_years', 0)),
                    department=record.get('department'),
                    designation=record.get('designation'),
                    phone=record['phone'],
                    address=record.get('address'),
                    emergency_contact_name=record.get('emergency_contact_name'),
                    emergency_contact_phone=record.get('emergency_contact_phone'),
                    auto_generated_email=email if auto_generated else None,
                    default_password_changed=False,
                    first_login_completed=False,
                    password_reset_required=True
                )
                
                # Handle optional date fields
                if record.get('joining_date'):
                    try:
                        from datetime import datetime
                        teacher.joining_date = datetime.strptime(
                            record['joining_date'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass
                
                if record.get('date_of_birth'):
                    try:
                        from datetime import datetime
                        teacher.date_of_birth = datetime.strptime(
                            record['date_of_birth'], '%Y-%m-%d'
                        ).date()
                    except:
                        pass
                
                db.add(teacher)
                
                created_teachers.append({
                    'teacher_id': teacher_id,
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'subject': record['subject_specialization'],
                    'qualification': record['qualification']
                })
                
                credentials_list.append({
                    'teacher_id': teacher_id,
                    'name': f"{first_name} {last_name}",
                    'email': email,
                    'password': password,
                    'auto_generated': auto_generated
                })
                
            except Exception as e:
                failed_teachers.append({
                    'teacher_id': record.get('teacher_id', 'Unknown'),
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
            "created_count": len(created_teachers),
            "failed_count": len(failed_teachers),
            "created_teachers": created_teachers,
            "failed_teachers": failed_teachers,
            "credentials": credentials_list if not send_credentials else []
        }
    
    def _send_bulk_credentials(self, credentials_list: List[Dict], institute_name: str):
        """Send login credentials to teachers via email"""
        
        for cred in credentials_list:
            try:
                email_content = f"""
                Dear {cred['name']},

                Welcome to MEDHASAKTHI! Your teacher account has been created for {institute_name}.

                Login Credentials:
                Email: {cred['email']}
                Password: {cred['password']}

                Important Notes:
                1. Please change your password on first login
                2. Keep these credentials secure
                3. Contact the institute admin for any issues

                Teacher Portal: https://medhasakthi.com/login

                Best regards,
                MEDHASAKTHI Team
                """
                
                email_service.send_email(
                    to_email=cred['email'],
                    subject=f"MEDHASAKTHI Teacher Account - {institute_name}",
                    content=email_content
                )
                
            except Exception as e:
                print(f"Failed to send credentials to {cred['teacher_id']}: {str(e)}")
    
    def generate_csv_template(self) -> str:
        """Generate CSV template for bulk teacher import"""
        
        headers = self.required_fields + self.optional_fields
        
        # Create sample data
        sample_data = {
            'teacher_id': 'TCH001',
            'first_name': 'John',
            'last_name': 'Smith',
            'subject_specialization': 'Mathematics',
            'qualification': 'M.Sc Mathematics, B.Ed',
            'experience_years': '5',
            'phone': '+91-9876543210',
            'email': 'john.smith@example.com',
            'employee_id': 'EMP001',
            'department': 'Science',
            'designation': 'Senior Teacher',
            'joining_date': '2020-06-15',
            'salary_grade': 'Grade-A',
            'address': '123 Teacher Colony, City, State - 123456',
            'emergency_contact_name': 'Jane Smith',
            'emergency_contact_phone': '+91-9876543211',
            'date_of_birth': '1985-03-20',
            'gender': 'Male',
            'blood_group': 'O+',
            'aadhar_number': '1234-5678-9012',
            'pan_number': 'ABCDE1234F',
            'classes_assigned': 'Class 9, Class 10',
            'subjects_assigned': 'Mathematics, Physics',
            'is_class_teacher': 'Yes',
            'class_teacher_of': 'Class 10-A'
        }
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        writer.writerow(sample_data)
        
        return output.getvalue()
    
    def get_teacher_credentials_report(self, institute_id: str, db: Session) -> List[Dict]:
        """Get report of all teachers with their login credentials"""
        
        teachers = db.query(Teacher).join(User).filter(
            Teacher.institute_id == institute_id,
            Teacher.is_active == True
        ).all()
        
        credentials_report = []
        for teacher in teachers:
            credentials_report.append({
                'teacher_id': teacher.teacher_id,
                'name': teacher.user.full_name,
                'email': teacher.auto_generated_email or teacher.user.email,
                'subject_specialization': teacher.subject_specialization,
                'qualification': teacher.qualification,
                'first_login_completed': teacher.first_login_completed,
                'password_changed': teacher.default_password_changed,
                'last_login': teacher.user.last_login_at.isoformat() if teacher.user.last_login_at else None,
                'is_active': teacher.is_active
            })
        
        return credentials_report


# Global instance
teacher_bulk_service = TeacherBulkService()
