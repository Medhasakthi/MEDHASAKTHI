"""
UPI Payment API routes for MEDHASAKTHI
Handle UPI payment requests, verification, and management
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_super_admin_user
from app.models.user import User
from app.services.upi_payment_service import upi_payment_service
from app.models.upi_payment import UPIConfiguration, UPIProvider

router = APIRouter()


@router.post("/create-payment")
async def create_upi_payment(
    payment_data: Dict[str, Any],
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new UPI payment request"""
    
    # Validate required fields
    required_fields = ["amount", "description"]
    for field in required_fields:
        if field not in payment_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # Prepare user data
    user_data = {
        "user_id": str(current_user.id) if current_user else None,
        "email": payment_data.get("email") or (current_user.email if current_user else None),
        "phone": payment_data.get("phone"),
        "name": payment_data.get("name") or (current_user.full_name if current_user else None),
        "metadata": payment_data.get("metadata", {}),
        "ip_address": payment_data.get("ip_address"),
        "user_agent": payment_data.get("user_agent")
    }
    
    # Validate email for guest users
    if not current_user and not user_data["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is required for guest payments"
        )
    
    payment_request = upi_payment_service.create_payment_request(
        amount=float(payment_data["amount"]),
        description=payment_data["description"],
        user_data=user_data,
        reference_id=payment_data.get("reference_id"),
        db=db
    )
    
    return {
        "status": "success",
        "data": payment_request
    }


@router.post("/submit-proof/{payment_id}")
async def submit_payment_proof(
    payment_id: str,
    transaction_id: str = Form(...),
    payment_method: Optional[str] = Form(None),
    screenshot: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Submit payment proof with screenshot"""
    
    screenshot_data = None
    if screenshot:
        # In a real application, you would save this to cloud storage
        # For now, we'll just store the filename
        screenshot_data = f"screenshots/{payment_id}_{screenshot.filename}"
        
        # TODO: Save file to storage service
        # screenshot_url = await save_to_storage(screenshot, screenshot_data)
    
    result = upi_payment_service.submit_payment_proof(
        payment_id=payment_id,
        transaction_id=transaction_id,
        screenshot_data=screenshot_data,
        payment_method=payment_method,
        db=db
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """Get payment status"""
    
    status_data = upi_payment_service.get_payment_status(payment_id, db)
    
    return {
        "status": "success",
        "data": status_data
    }


@router.get("/my-payments")
async def get_user_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's payment history"""
    
    from app.models.upi_payment import UPIPaymentRequest
    
    payments = db.query(UPIPaymentRequest).filter(
        UPIPaymentRequest.user_id == current_user.id
    ).order_by(UPIPaymentRequest.created_at.desc()).all()
    
    payments_data = []
    for payment in payments:
        payments_data.append({
            "payment_id": payment.payment_id,
            "amount": float(payment.amount),
            "description": payment.description,
            "status": payment.status.value,
            "verification_status": payment.verification_status,
            "created_at": payment.created_at.isoformat(),
            "paid_at": payment.paid_at.isoformat() if payment.paid_at else None,
            "verified_at": payment.verified_at.isoformat() if payment.verified_at else None,
            "transaction_id": payment.transaction_id,
            "reference_id": payment.reference_id
        })
    
    return {
        "status": "success",
        "data": {
            "payments": payments_data,
            "total_count": len(payments_data)
        }
    }


# Admin routes for payment verification
@router.get("/admin/pending-verifications")
async def get_pending_verifications(
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Get payments pending verification (Admin only)"""
    
    pending_payments = upi_payment_service.get_pending_verifications(db)
    
    return {
        "status": "success",
        "data": {
            "pending_payments": pending_payments,
            "total_count": len(pending_payments)
        }
    }


@router.post("/admin/verify/{payment_id}")
async def verify_payment(
    payment_id: str,
    verification_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Verify payment (Admin only)"""
    
    if "verification_status" not in verification_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="verification_status is required"
        )
    
    if verification_data["verification_status"] not in ["verified", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="verification_status must be 'verified' or 'rejected'"
        )
    
    result = upi_payment_service.verify_payment(
        payment_id=payment_id,
        verification_status=verification_data["verification_status"],
        verified_by=current_user.email,
        notes=verification_data.get("notes"),
        db=db
    )
    
    return {
        "status": "success",
        "data": result
    }


# Super admin routes for UPI configuration
@router.post("/admin/config")
async def create_upi_config(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Create UPI configuration (Super Admin only)"""
    
    required_fields = ["upi_id", "upi_name", "provider"]
    for field in required_fields:
        if field not in config_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    try:
        # If this is set as primary, deactivate other primary configs
        if config_data.get("is_primary", False):
            db.query(UPIConfiguration).filter(
                UPIConfiguration.is_primary == True
            ).update({"is_primary": False})
        
        upi_config = UPIConfiguration(
            upi_id=config_data["upi_id"],
            upi_name=config_data["upi_name"],
            provider=UPIProvider(config_data["provider"]),
            is_active=config_data.get("is_active", True),
            is_primary=config_data.get("is_primary", False),
            display_name=config_data.get("display_name"),
            description=config_data.get("description"),
            min_amount=config_data.get("min_amount", 1.00),
            max_amount=config_data.get("max_amount", 100000.00),
            daily_limit=config_data.get("daily_limit"),
            auto_generate_qr=config_data.get("auto_generate_qr", True),
            include_amount_in_qr=config_data.get("include_amount_in_qr", True),
            include_note_in_qr=config_data.get("include_note_in_qr", True),
            require_screenshot=config_data.get("require_screenshot", True),
            auto_verify_payments=config_data.get("auto_verify_payments", False),
            verification_timeout_minutes=config_data.get("verification_timeout_minutes", 30),
            notify_on_payment=config_data.get("notify_on_payment", True),
            notification_email=config_data.get("notification_email"),
            notification_phone=config_data.get("notification_phone"),
            created_by=current_user.email
        )
        
        db.add(upi_config)
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "config_id": str(upi_config.id),
                "message": "UPI configuration created successfully"
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create UPI configuration: {str(e)}"
        )


@router.get("/admin/config")
async def get_upi_configs(
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Get all UPI configurations (Super Admin only)"""
    
    configs = db.query(UPIConfiguration).order_by(
        UPIConfiguration.is_primary.desc(),
        UPIConfiguration.created_at.desc()
    ).all()
    
    configs_data = []
    for config in configs:
        configs_data.append({
            "id": str(config.id),
            "upi_id": config.upi_id,
            "upi_name": config.upi_name,
            "provider": config.provider.value,
            "is_active": config.is_active,
            "is_primary": config.is_primary,
            "display_name": config.display_name,
            "description": config.description,
            "min_amount": float(config.min_amount),
            "max_amount": float(config.max_amount),
            "daily_limit": float(config.daily_limit) if config.daily_limit else None,
            "require_screenshot": config.require_screenshot,
            "auto_verify_payments": config.auto_verify_payments,
            "verification_timeout_minutes": config.verification_timeout_minutes,
            "total_transactions": config.total_transactions,
            "total_amount": float(config.total_amount),
            "success_rate": float(config.success_rate),
            "created_at": config.created_at.isoformat(),
            "created_by": config.created_by
        })
    
    return {
        "status": "success",
        "data": {
            "configurations": configs_data,
            "total_count": len(configs_data)
        }
    }


@router.put("/admin/config/{config_id}")
async def update_upi_config(
    config_id: str,
    config_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Update UPI configuration (Super Admin only)"""
    
    config = db.query(UPIConfiguration).filter(
        UPIConfiguration.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UPI configuration not found"
        )
    
    try:
        # If setting as primary, deactivate other primary configs
        if config_data.get("is_primary", False) and not config.is_primary:
            db.query(UPIConfiguration).filter(
                UPIConfiguration.is_primary == True
            ).update({"is_primary": False})
        
        # Update allowed fields
        updatable_fields = [
            "upi_name", "is_active", "is_primary", "display_name", "description",
            "min_amount", "max_amount", "daily_limit", "auto_generate_qr",
            "include_amount_in_qr", "include_note_in_qr", "require_screenshot",
            "auto_verify_payments", "verification_timeout_minutes", "notify_on_payment",
            "notification_email", "notification_phone"
        ]
        
        for field in updatable_fields:
            if field in config_data:
                setattr(config, field, config_data[field])
        
        db.commit()
        
        return {
            "status": "success",
            "message": "UPI configuration updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update UPI configuration: {str(e)}"
        )


@router.delete("/admin/config/{config_id}")
async def delete_upi_config(
    config_id: str,
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Delete UPI configuration (Super Admin only)"""
    
    config = db.query(UPIConfiguration).filter(
        UPIConfiguration.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="UPI configuration not found"
        )
    
    if config.is_primary:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete primary UPI configuration"
        )
    
    try:
        db.delete(config)
        db.commit()
        
        return {
            "status": "success",
            "message": "UPI configuration deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete UPI configuration: {str(e)}"
        )


@router.get("/admin/analytics")
async def get_upi_analytics(
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Get UPI payment analytics (Super Admin only)"""
    
    from app.models.upi_payment import UPIPaymentRequest
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    # Get analytics for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    # Total payments
    total_payments = db.query(UPIPaymentRequest).count()
    
    # Recent payments (last 30 days)
    recent_payments = db.query(UPIPaymentRequest).filter(
        UPIPaymentRequest.created_at >= thirty_days_ago
    ).count()
    
    # Successful payments
    successful_payments = db.query(UPIPaymentRequest).filter(
        UPIPaymentRequest.status == "success"
    ).count()
    
    # Total amount
    total_amount = db.query(func.sum(UPIPaymentRequest.amount)).filter(
        UPIPaymentRequest.status == "success"
    ).scalar() or 0
    
    # Success rate
    success_rate = (successful_payments / total_payments * 100) if total_payments > 0 else 0
    
    # Pending verifications
    pending_verifications = db.query(UPIPaymentRequest).filter(
        UPIPaymentRequest.verification_status == "pending"
    ).count()
    
    return {
        "status": "success",
        "data": {
            "total_payments": total_payments,
            "recent_payments": recent_payments,
            "successful_payments": successful_payments,
            "total_amount": float(total_amount),
            "success_rate": round(success_rate, 2),
            "pending_verifications": pending_verifications,
            "period": "last_30_days"
        }
    }
