"""
Teacher Bulk Management API routes for MEDHASAKTHI
Institute-specific bulk teacher operations and credential management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional
import io
import csv

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_institute_admin_user
from app.models.user import User
from app.services.teacher_bulk_service import teacher_bulk_service

router = APIRouter()


@router.get("/template/download")
async def download_teacher_csv_template(
    current_user: User = Depends(get_institute_admin_user)
):
    """Download CSV template for bulk teacher import"""
    
    template_content = teacher_bulk_service.generate_csv_template()
    
    return StreamingResponse(
        io.StringIO(template_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teacher_bulk_import_template.csv"}
    )


@router.post("/validate-csv")
async def validate_teacher_csv_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Validate CSV file for bulk teacher import"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Process and validate
    try:
        csv_string = file_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        csv_data = list(csv_reader)
        
        validation_result = teacher_bulk_service.validate_csv_data(csv_data)
        
        return {
            "status": "success" if validation_result["valid"] else "error",
            "data": validation_result
        }
        
    except Exception as e:
        return {
            "status": "error",
            "data": {
                "valid": False,
                "errors": [f"Error processing CSV file: {str(e)}"],
                "warnings": [],
                "valid_records": [],
                "total_records": 0
            }
        }


@router.post("/import")
async def bulk_import_teachers(
    file: UploadFile = File(...),
    send_credentials: bool = Form(True),
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk import teachers from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read and validate file
    file_content = await file.read()
    
    try:
        csv_string = file_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        csv_data = list(csv_reader)
        
        validation_result = teacher_bulk_service.validate_csv_data(csv_data)
        
        if not validation_result["valid"]:
            return {
                "status": "error",
                "message": "CSV validation failed",
                "data": validation_result
            }
        
        # Import teachers
        import_result = teacher_bulk_service.bulk_import_teachers(
            validation_result["valid_records"],
            current_user.institute_id,
            db,
            send_credentials
        )
        
        return {
            "status": "success",
            "message": f"Successfully imported {import_result['created_count']} teachers",
            "data": import_result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}"
        )


@router.get("/credentials-report")
async def get_teacher_credentials_report(
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Get report of all teacher credentials"""
    
    report = teacher_bulk_service.get_teacher_credentials_report(
        current_user.institute_id, db
    )
    
    return {
        "status": "success",
        "data": {
            "teachers": report,
            "total_count": len(report),
            "institute_id": current_user.institute_id
        }
    }


@router.get("/credentials-report/download")
async def download_teacher_credentials_report(
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Download teacher credentials report as CSV"""
    
    report = teacher_bulk_service.get_teacher_credentials_report(
        current_user.institute_id, db
    )
    
    # Create CSV content
    output = io.StringIO()
    if report:
        fieldnames = ['teacher_id', 'name', 'email', 'subject_specialization', 
                     'qualification', 'first_login_completed', 'password_changed', 'last_login']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report)
    
    csv_content = output.getvalue()
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=teacher_credentials_report.csv"}
    )


@router.post("/reset-password/{teacher_id}")
async def reset_teacher_password(
    teacher_id: str,
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Reset teacher password to default"""
    
    from app.models.user import Teacher, Institute
    from app.core.security import get_password_hash
    import re
    
    # Get teacher
    teacher = db.query(Teacher).join(User).filter(
        Teacher.teacher_id == teacher_id,
        Teacher.institute_id == current_user.institute_id
    ).first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Get institute name for password generation
    institute = db.query(Institute).filter(Institute.id == current_user.institute_id).first()
    clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute.name.lower())
    new_password = f"{clean_institute_name}@123"
    
    # Update password
    teacher.user.password_hash = get_password_hash(new_password)
    teacher.default_password_changed = False
    teacher.password_reset_required = True
    
    db.commit()
    
    return {
        "status": "success",
        "data": {
            "teacher_id": teacher_id,
            "new_password": new_password,
            "message": "Password reset successfully"
        }
    }


@router.post("/bulk-reset-passwords")
async def bulk_reset_teacher_passwords(
    teacher_ids: List[str],
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Reset passwords for multiple teachers"""
    
    results = []
    failed = []
    
    for teacher_id in teacher_ids:
        try:
            # Use the existing reset logic
            from app.models.user import Teacher, Institute
            from app.core.security import get_password_hash
            import re
            
            teacher = db.query(Teacher).join(User).filter(
                Teacher.teacher_id == teacher_id,
                Teacher.institute_id == current_user.institute_id
            ).first()
            
            if not teacher:
                failed.append({
                    "teacher_id": teacher_id,
                    "error": "Teacher not found"
                })
                continue
            
            institute = db.query(Institute).filter(Institute.id == current_user.institute_id).first()
            clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute.name.lower())
            new_password = f"{clean_institute_name}@123"
            
            teacher.user.password_hash = get_password_hash(new_password)
            teacher.default_password_changed = False
            teacher.password_reset_required = True
            
            results.append({
                "teacher_id": teacher_id,
                "new_password": new_password,
                "message": "Password reset successfully"
            })
            
        except Exception as e:
            failed.append({
                "teacher_id": teacher_id,
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "status": "success",
        "data": {
            "reset_count": len(results),
            "failed_count": len(failed),
            "reset_teachers": results,
            "failed_teachers": failed
        }
    }


@router.post("/send-credentials/{teacher_id}")
async def resend_teacher_credentials(
    teacher_id: str,
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Resend login credentials to specific teacher"""
    
    from app.models.user import Teacher, Institute
    from app.services.email_service import email_service
    import re
    
    # Get teacher details
    teacher = db.query(Teacher).join(User).filter(
        Teacher.teacher_id == teacher_id,
        Teacher.institute_id == current_user.institute_id
    ).first()
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    # Get institute details
    institute = db.query(Institute).filter(
        Institute.id == current_user.institute_id
    ).first()
    
    # Generate current password (default format)
    clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute.name.lower())
    current_password = f"{clean_institute_name}@123"
    
    # Send credentials email
    try:
        email_content = f"""
        Dear {teacher.user.full_name},

        Your MEDHASAKTHI teacher account credentials for {institute.name}:

        Email: {teacher.auto_generated_email or teacher.user.email}
        Password: {current_password}

        Please change your password on first login for security.

        Teacher Portal: https://medhasakthi.com/login

        Best regards,
        {institute.name}
        """
        
        email_service.send_email(
            to_email=teacher.user.email,
            subject=f"MEDHASAKTHI Teacher Credentials - {institute.name}",
            content=email_content
        )
        
        return {
            "status": "success",
            "message": f"Credentials sent to {teacher.user.email}",
            "data": {
                "teacher_id": teacher_id,
                "email_sent_to": teacher.user.email
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send credentials: {str(e)}"
        )


@router.get("/statistics")
async def get_teacher_bulk_statistics(
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Get statistics for teacher bulk operations"""
    
    from app.models.user import Teacher
    from sqlalchemy import func, and_
    
    # Get teacher statistics
    total_teachers = db.query(Teacher).filter(
        Teacher.institute_id == current_user.institute_id,
        Teacher.is_active == True
    ).count()
    
    teachers_with_default_password = db.query(Teacher).filter(
        and_(
            Teacher.institute_id == current_user.institute_id,
            Teacher.is_active == True,
            Teacher.default_password_changed == False
        )
    ).count()
    
    teachers_first_login_pending = db.query(Teacher).filter(
        and_(
            Teacher.institute_id == current_user.institute_id,
            Teacher.is_active == True,
            Teacher.first_login_completed == False
        )
    ).count()
    
    # Department-wise distribution
    dept_distribution = db.query(
        Teacher.department,
        func.count(Teacher.id).label('count')
    ).filter(
        Teacher.institute_id == current_user.institute_id,
        Teacher.is_active == True
    ).group_by(Teacher.department).all()
    
    # Subject-wise distribution
    subject_distribution = db.query(
        Teacher.subject_specialization,
        func.count(Teacher.id).label('count')
    ).filter(
        Teacher.institute_id == current_user.institute_id,
        Teacher.is_active == True
    ).group_by(Teacher.subject_specialization).all()
    
    return {
        "status": "success",
        "data": {
            "total_teachers": total_teachers,
            "teachers_with_default_password": teachers_with_default_password,
            "teachers_first_login_pending": teachers_first_login_pending,
            "password_change_rate": round(
                ((total_teachers - teachers_with_default_password) / total_teachers * 100) 
                if total_teachers > 0 else 0, 2
            ),
            "first_login_rate": round(
                ((total_teachers - teachers_first_login_pending) / total_teachers * 100)
                if total_teachers > 0 else 0, 2
            ),
            "department_distribution": [
                {
                    "department": dist.department or "Not Assigned",
                    "count": dist.count
                }
                for dist in dept_distribution
            ],
            "subject_distribution": [
                {
                    "subject": dist.subject_specialization or "Not Assigned",
                    "count": dist.count
                }
                for dist in subject_distribution
            ]
        }
    }
