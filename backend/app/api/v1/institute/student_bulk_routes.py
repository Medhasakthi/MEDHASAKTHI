"""
Student Bulk Management API routes for MEDHASAKTHI
Institute-specific bulk student operations and credential management
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
from app.services.student_bulk_service import student_bulk_service

router = APIRouter()


@router.get("/template/download")
async def download_csv_template(
    current_user: User = Depends(get_institute_admin_user)
):
    """Download CSV template for bulk student import"""
    
    template_content = student_bulk_service.generate_csv_template()
    
    # Create streaming response
    def generate():
        yield template_content
    
    return StreamingResponse(
        io.StringIO(template_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_bulk_import_template.csv"}
    )


@router.post("/validate-csv")
async def validate_csv_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Validate CSV file for bulk student import"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Process and validate
    validation_result = student_bulk_service.process_csv_file(
        file_content, current_user.institute_id, db
    )
    
    return {
        "status": "success" if validation_result["valid"] else "error",
        "data": validation_result
    }


@router.post("/import")
async def bulk_import_students(
    file: UploadFile = File(...),
    send_credentials: bool = Form(True),
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Bulk import students from CSV file"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed"
        )
    
    # Read and validate file
    file_content = await file.read()
    validation_result = student_bulk_service.process_csv_file(
        file_content, current_user.institute_id, db
    )
    
    if not validation_result["valid"]:
        return {
            "status": "error",
            "message": "CSV validation failed",
            "data": validation_result
        }
    
    # Import students
    import_result = student_bulk_service.bulk_import_students(
        validation_result["valid_records"],
        current_user.institute_id,
        db,
        send_credentials
    )
    
    return {
        "status": "success",
        "message": f"Successfully imported {import_result['created_count']} students",
        "data": import_result
    }


@router.get("/credentials-report")
async def get_credentials_report(
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Get report of all student credentials"""
    
    report = student_bulk_service.get_student_credentials_report(
        current_user.institute_id, db
    )
    
    return {
        "status": "success",
        "data": {
            "students": report,
            "total_count": len(report),
            "institute_id": current_user.institute_id
        }
    }


@router.get("/credentials-report/download")
async def download_credentials_report(
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Download credentials report as CSV"""
    
    report = student_bulk_service.get_student_credentials_report(
        current_user.institute_id, db
    )
    
    # Create CSV content
    output = io.StringIO()
    if report:
        fieldnames = ['student_id', 'name', 'email', 'class', 'section', 
                     'first_login_completed', 'password_changed', 'last_login']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report)
    
    csv_content = output.getvalue()
    
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=student_credentials_report.csv"}
    )


@router.post("/reset-password/{student_id}")
async def reset_student_password(
    student_id: str,
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Reset student password to default"""
    
    result = student_bulk_service.reset_student_password(
        student_id, current_user.institute_id, db
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.post("/bulk-reset-passwords")
async def bulk_reset_passwords(
    student_ids: List[str],
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Reset passwords for multiple students"""
    
    results = []
    failed = []
    
    for student_id in student_ids:
        try:
            result = student_bulk_service.reset_student_password(
                student_id, current_user.institute_id, db
            )
            results.append(result)
        except Exception as e:
            failed.append({
                "student_id": student_id,
                "error": str(e)
            })
    
    return {
        "status": "success",
        "data": {
            "reset_count": len(results),
            "failed_count": len(failed),
            "reset_students": results,
            "failed_students": failed
        }
    }


@router.get("/import-history")
async def get_import_history(
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Get history of bulk imports"""
    
    # This would typically fetch from an import_history table
    # For now, return mock data
    
    history = [
        {
            "id": "import_001",
            "filename": "students_batch_1.csv",
            "imported_count": 150,
            "failed_count": 5,
            "imported_by": current_user.full_name,
            "imported_at": "2024-01-15T10:30:00Z",
            "status": "completed"
        },
        {
            "id": "import_002", 
            "filename": "students_batch_2.csv",
            "imported_count": 200,
            "failed_count": 0,
            "imported_by": current_user.full_name,
            "imported_at": "2024-01-10T14:20:00Z",
            "status": "completed"
        }
    ]
    
    # Apply pagination
    start = (page - 1) * limit
    end = start + limit
    paginated_history = history[start:end]
    
    return {
        "status": "success",
        "data": {
            "imports": paginated_history,
            "pagination": {
                "current_page": page,
                "total_pages": (len(history) + limit - 1) // limit,
                "total_items": len(history),
                "items_per_page": limit
            }
        }
    }


@router.get("/statistics")
async def get_bulk_import_statistics(
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Get statistics for bulk import operations"""
    
    from app.models.user import Student
    from sqlalchemy import func, and_
    
    # Get student statistics
    total_students = db.query(Student).filter(
        Student.institute_id == current_user.institute_id,
        Student.is_active == True
    ).count()
    
    students_with_default_password = db.query(Student).filter(
        and_(
            Student.institute_id == current_user.institute_id,
            Student.is_active == True,
            Student.default_password_changed == False
        )
    ).count()
    
    students_first_login_pending = db.query(Student).filter(
        and_(
            Student.institute_id == current_user.institute_id,
            Student.is_active == True,
            Student.first_login_completed == False
        )
    ).count()
    
    # Class-wise distribution
    class_distribution = db.query(
        Student.class_level,
        func.count(Student.id).label('count')
    ).filter(
        Student.institute_id == current_user.institute_id,
        Student.is_active == True
    ).group_by(Student.class_level).all()
    
    return {
        "status": "success",
        "data": {
            "total_students": total_students,
            "students_with_default_password": students_with_default_password,
            "students_first_login_pending": students_first_login_pending,
            "password_change_rate": round(
                ((total_students - students_with_default_password) / total_students * 100) 
                if total_students > 0 else 0, 2
            ),
            "first_login_rate": round(
                ((total_students - students_first_login_pending) / total_students * 100)
                if total_students > 0 else 0, 2
            ),
            "class_distribution": [
                {
                    "class": dist.class_level,
                    "count": dist.count
                }
                for dist in class_distribution
            ]
        }
    }


@router.post("/send-credentials/{student_id}")
async def resend_credentials(
    student_id: str,
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Resend login credentials to specific student"""
    
    from app.models.user import Student, Institute
    from app.services.email_service import email_service
    
    # Get student details
    student = db.query(Student).join(User).filter(
        and_(
            Student.student_id == student_id,
            Student.institute_id == current_user.institute_id
        )
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Get institute details
    institute = db.query(Institute).filter(
        Institute.id == current_user.institute_id
    ).first()
    
    # Generate current password (default format)
    import re
    clean_institute_name = re.sub(r'[^a-zA-Z0-9]', '', institute.name.lower())
    current_password = f"{clean_institute_name}@123"
    
    # Send credentials email
    try:
        email_content = f"""
        Dear Parent/Guardian,

        Login credentials for {student.user.full_name} (Student ID: {student.student_id}):

        Email: {student.auto_generated_email or student.user.email}
        Password: {current_password}

        Please ensure the student changes the password on first login.

        Login at: https://medhasakthi.com/login

        Best regards,
        {institute.name}
        """
        
        # Send to guardian email if available, otherwise to student email
        recipient_email = student.guardian_email or student.user.email
        
        email_service.send_email(
            to_email=recipient_email,
            subject=f"MEDHASAKTHI Login Credentials - {institute.name}",
            content=email_content
        )
        
        return {
            "status": "success",
            "message": f"Credentials sent to {recipient_email}",
            "data": {
                "student_id": student_id,
                "email_sent_to": recipient_email
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send credentials: {str(e)}"
        )


@router.post("/bulk-send-credentials")
async def bulk_send_credentials(
    student_ids: List[str],
    current_user: User = Depends(get_institute_admin_user),
    db: Session = Depends(get_db)
):
    """Send credentials to multiple students"""
    
    sent_count = 0
    failed_count = 0
    results = []
    
    for student_id in student_ids:
        try:
            # Use the existing resend_credentials logic
            result = await resend_credentials(student_id, current_user, db)
            sent_count += 1
            results.append({
                "student_id": student_id,
                "status": "sent",
                "email": result["data"]["email_sent_to"]
            })
        except Exception as e:
            failed_count += 1
            results.append({
                "student_id": student_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "status": "success",
        "data": {
            "sent_count": sent_count,
            "failed_count": failed_count,
            "results": results
        }
    }
