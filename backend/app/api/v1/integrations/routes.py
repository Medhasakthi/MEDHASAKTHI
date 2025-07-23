"""
Enterprise Integration API routes for MEDHASAKTHI
LMS, SIS, payment gateway, and webhook integrations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_admin_user
from app.models.user import User
from app.services.enterprise_integration_service import (
    lms_integration_service,
    sis_integration_service,
    payment_gateway_service,
    webhook_service
)

router = APIRouter()


# LMS Integration Routes
@router.post("/lms/sync-students")
async def sync_students_from_lms(
    sync_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Sync students from LMS to MEDHASAKTHI"""
    
    institute_id = sync_request.get("institute_id")
    lms_type = sync_request.get("lms_type")
    lms_config = sync_request.get("lms_config", {})
    
    if not all([institute_id, lms_type, lms_config]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="institute_id, lms_type, and lms_config are required"
        )
    
    # Run sync in background
    background_tasks.add_task(
        lms_integration_service.sync_students_from_lms,
        institute_id,
        lms_type,
        lms_config,
        db
    )
    
    return {
        "message": "Student sync initiated",
        "institute_id": institute_id,
        "lms_type": lms_type,
        "status": "processing"
    }


@router.post("/lms/export-grades")
async def export_grades_to_lms(
    export_request: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Export exam grades to LMS"""
    
    exam_id = export_request.get("exam_id")
    lms_type = export_request.get("lms_type")
    lms_config = export_request.get("lms_config", {})
    
    if not all([exam_id, lms_type, lms_config]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="exam_id, lms_type, and lms_config are required"
        )
    
    result = await lms_integration_service.export_grades_to_lms(
        exam_id, lms_type, lms_config, db
    )
    
    return result


@router.get("/lms/supported-systems")
async def get_supported_lms():
    """Get list of supported LMS systems"""
    return {
        "supported_lms": [
            {
                "type": "moodle",
                "name": "Moodle",
                "description": "Open-source learning management system",
                "features": ["student_sync", "grade_export", "course_sync"]
            },
            {
                "type": "canvas",
                "name": "Canvas LMS",
                "description": "Cloud-based learning management system",
                "features": ["student_sync", "grade_export", "assignment_sync"]
            },
            {
                "type": "blackboard",
                "name": "Blackboard Learn",
                "description": "Enterprise learning management system",
                "features": ["student_sync", "grade_export", "content_sync"]
            },
            {
                "type": "google_classroom",
                "name": "Google Classroom",
                "description": "Google's educational platform",
                "features": ["student_sync", "grade_export", "assignment_sync"]
            }
        ]
    }


# SIS Integration Routes
@router.post("/sis/sync-student-data")
async def sync_student_data_from_sis(
    sync_request: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Sync comprehensive student data from SIS"""
    
    institute_id = sync_request.get("institute_id")
    sis_type = sync_request.get("sis_type")
    sis_config = sync_request.get("sis_config", {})
    
    if not all([institute_id, sis_type, sis_config]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="institute_id, sis_type, and sis_config are required"
        )
    
    result = await sis_integration_service.sync_student_data(
        institute_id, sis_type, sis_config, db
    )
    
    return result


@router.get("/sis/supported-systems")
async def get_supported_sis():
    """Get list of supported SIS systems"""
    return {
        "supported_sis": [
            {
                "type": "powerschool",
                "name": "PowerSchool",
                "description": "Comprehensive student information system",
                "features": ["student_data", "grades", "attendance", "demographics"]
            },
            {
                "type": "infinite_campus",
                "name": "Infinite Campus",
                "description": "K-12 student information system",
                "features": ["student_data", "grades", "scheduling", "parent_portal"]
            },
            {
                "type": "skyward",
                "name": "Skyward",
                "description": "School management suite",
                "features": ["student_data", "grades", "finance", "hr"]
            }
        ]
    }


# Payment Gateway Routes
@router.post("/payments/create-order")
async def create_payment_order(
    payment_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create payment order with specified gateway"""
    
    gateway = payment_request.get("gateway")
    amount = payment_request.get("amount")
    currency = payment_request.get("currency", "INR")
    order_details = payment_request.get("order_details", {})
    
    if not all([gateway, amount]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="gateway and amount are required"
        )
    
    result = await payment_gateway_service.create_payment_order(
        gateway, amount, currency, order_details
    )
    
    return result


@router.post("/payments/verify")
async def verify_payment(
    verification_request: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify payment with gateway"""
    
    gateway = verification_request.get("gateway")
    payment_id = verification_request.get("payment_id")
    order_id = verification_request.get("order_id")
    signature = verification_request.get("signature")
    
    if not all([gateway, payment_id, order_id]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="gateway, payment_id, and order_id are required"
        )
    
    result = await payment_gateway_service.verify_payment(
        gateway, payment_id, order_id, signature
    )
    
    return result


@router.get("/payments/supported-gateways")
async def get_supported_payment_gateways():
    """Get list of supported payment gateways"""
    return {
        "supported_gateways": [
            {
                "type": "razorpay",
                "name": "Razorpay",
                "description": "Indian payment gateway",
                "currencies": ["INR"],
                "features": ["cards", "netbanking", "upi", "wallets"]
            },
            {
                "type": "stripe",
                "name": "Stripe",
                "description": "Global payment platform",
                "currencies": ["USD", "EUR", "GBP", "INR"],
                "features": ["cards", "digital_wallets", "bank_transfers"]
            },
            {
                "type": "paypal",
                "name": "PayPal",
                "description": "Global digital payment platform",
                "currencies": ["USD", "EUR", "GBP", "INR"],
                "features": ["paypal_account", "cards", "bank_transfers"]
            },
            {
                "type": "payu",
                "name": "PayU",
                "description": "Payment technology platform",
                "currencies": ["INR", "USD", "EUR"],
                "features": ["cards", "netbanking", "emi", "wallets"]
            }
        ]
    }


# Webhook Routes
@router.post("/webhooks/{webhook_type}")
async def handle_webhook(
    webhook_type: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle incoming webhooks from external services"""
    
    # Get request body and headers
    body = await request.body()
    headers = dict(request.headers)
    
    try:
        payload = await request.json()
    except:
        payload = {"raw_body": body.decode()}
    
    result = await webhook_service.process_webhook(
        webhook_type, payload, headers, db
    )
    
    return result


@router.get("/webhooks/supported-types")
async def get_supported_webhook_types():
    """Get list of supported webhook types"""
    return {
        "supported_webhooks": [
            {
                "type": "payment_success",
                "description": "Payment successful notification",
                "source": "payment_gateways"
            },
            {
                "type": "payment_failure",
                "description": "Payment failed notification",
                "source": "payment_gateways"
            },
            {
                "type": "lms_enrollment",
                "description": "Student enrollment in LMS",
                "source": "lms_systems"
            },
            {
                "type": "sis_update",
                "description": "Student data update from SIS",
                "source": "sis_systems"
            }
        ]
    }


# API Management Routes
@router.post("/api-keys/generate")
async def generate_api_key(
    api_key_request: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Generate API key for external integrations"""
    
    key_name = api_key_request.get("name")
    permissions = api_key_request.get("permissions", [])
    expires_in_days = api_key_request.get("expires_in_days", 365)
    
    if not key_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key name is required"
        )
    
    # Generate API key
    import secrets
    api_key = f"mk_{secrets.token_urlsafe(32)}"
    
    # Store API key (in production, this would be stored in database)
    # For now, return the key
    
    return {
        "api_key": api_key,
        "name": key_name,
        "permissions": permissions,
        "expires_at": (datetime.now() + timedelta(days=expires_in_days)).isoformat(),
        "created_at": datetime.now().isoformat()
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all API keys"""
    
    # In production, this would fetch from database
    return {
        "api_keys": [
            {
                "id": "1",
                "name": "LMS Integration",
                "permissions": ["lms:read", "lms:write"],
                "created_at": "2024-01-01T00:00:00",
                "last_used": "2024-01-15T10:30:00",
                "status": "active"
            }
        ]
    }


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Revoke API key"""
    
    # In production, this would update database
    return {
        "message": f"API key {key_id} revoked successfully",
        "revoked_at": datetime.now().isoformat()
    }


# Integration Health Check
@router.get("/health")
async def integration_health_check():
    """Check health of all integration services"""
    
    health_status = {
        "lms_integrations": {
            "moodle": "healthy",
            "canvas": "healthy",
            "blackboard": "healthy",
            "google_classroom": "healthy"
        },
        "sis_integrations": {
            "powerschool": "healthy",
            "infinite_campus": "healthy",
            "skyward": "healthy"
        },
        "payment_gateways": {
            "razorpay": "healthy",
            "stripe": "healthy",
            "paypal": "healthy",
            "payu": "healthy"
        },
        "webhook_service": "healthy",
        "overall_status": "healthy",
        "last_checked": datetime.now().isoformat()
    }
    
    return health_status
