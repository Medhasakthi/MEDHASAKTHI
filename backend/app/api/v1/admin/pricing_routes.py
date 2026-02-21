"""
Super Admin Pricing Management API routes for MEDHASAKTHI
Configure pricing for independent learners
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user, get_super_admin_user
from app.models.user import User
from app.services.independent_learner_service import pricing_management_service
from app.models.pricing_config import GlobalPricingConfig, DiscountCoupon, ProgramPricingOverride
from app.models.independent_learner import CertificationProgram

router = APIRouter()


@router.post("/global-config")
async def create_global_pricing_config(
    config_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Create new global pricing configuration"""
    
    result = pricing_management_service.create_global_pricing_config(
        config_data, current_user.email, db
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/global-config")
async def get_global_pricing_config(
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Get current global pricing configuration"""
    
    config = db.query(GlobalPricingConfig).filter(
        GlobalPricingConfig.is_active == True,
        GlobalPricingConfig.approval_status == "active"
    ).order_by(GlobalPricingConfig.created_at.desc()).first()
    
    if not config:
        return {
            "status": "success",
            "data": None,
            "message": "No active pricing configuration found"
        }
    
    config_data = {
        "id": str(config.id),
        "config_name": config.config_name,
        "config_version": config.config_version,
        "description": config.description,
        "base_pricing": {
            "base_exam_fee": float(config.base_exam_fee),
            "base_certification_fee": float(config.base_certification_fee),
            "base_retake_fee": float(config.base_retake_fee),
            "primary_currency": config.primary_currency
        },
        "category_multipliers": {
            "student_multiplier": float(config.student_multiplier),
            "professional_multiplier": float(config.professional_multiplier),
            "enterprise_multiplier": float(config.enterprise_multiplier),
            "premium_multiplier": float(config.premium_multiplier)
        },
        "geographic_pricing": {
            "country_pricing_multipliers": config.country_pricing_multipliers,
            "state_pricing_multipliers": config.state_pricing_multipliers,
            "city_tier_multipliers": config.city_tier_multipliers
        },
        "discount_config": {
            "bulk_discount_config": config.bulk_discount_config,
            "referral_discount_percent": config.referral_discount_percent,
            "loyalty_discount_config": config.loyalty_discount_config
        },
        "payment_config": {
            "gateway_charges_config": config.gateway_charges_config,
            "convenience_fee_percent": float(config.convenience_fee_percent),
            "tax_config": config.tax_config,
            "tax_inclusive_pricing": config.tax_inclusive_pricing
        },
        "metadata": {
            "effective_from": config.effective_from.isoformat(),
            "effective_until": config.effective_until.isoformat() if config.effective_until else None,
            "created_by": config.created_by,
            "approved_by": config.approved_by,
            "approval_date": config.approval_date.isoformat() if config.approval_date else None
        }
    }
    
    return {
        "status": "success",
        "data": config_data
    }


@router.put("/global-config/{config_id}")
async def update_global_pricing_config(
    config_id: str,
    config_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Update existing global pricing configuration"""
    
    config = db.query(GlobalPricingConfig).filter(
        GlobalPricingConfig.id == config_id
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing configuration not found"
        )
    
    # Update fields
    updatable_fields = [
        'config_name', 'description', 'base_exam_fee', 'base_certification_fee',
        'base_retake_fee', 'student_multiplier', 'professional_multiplier',
        'enterprise_multiplier', 'premium_multiplier', 'country_pricing_multipliers',
        'state_pricing_multipliers', 'city_tier_multipliers', 'bulk_discount_config',
        'referral_discount_percent', 'loyalty_discount_config', 'gateway_charges_config',
        'convenience_fee_percent', 'tax_config', 'tax_inclusive_pricing'
    ]
    
    for field in updatable_fields:
        if field in config_data:
            setattr(config, field, config_data[field])
    
    try:
        db.commit()
        return {
            "status": "success",
            "message": "Pricing configuration updated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update configuration: {str(e)}"
        )


@router.post("/coupons")
async def create_discount_coupon(
    coupon_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Create new discount coupon"""
    
    result = pricing_management_service.create_discount_coupon(
        coupon_data, current_user.email, db
    )
    
    return {
        "status": "success",
        "data": result
    }


@router.get("/coupons")
async def get_discount_coupons(
    status: Optional[str] = Query(None, description="Filter by coupon status"),
    campaign: Optional[str] = Query(None, description="Filter by campaign"),
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Get all discount coupons"""
    
    query = db.query(DiscountCoupon)
    
    if status:
        if status == "active":
            query = query.filter(
                DiscountCoupon.is_active == True,
                DiscountCoupon.valid_until >= func.now()
            )
        elif status == "expired":
            query = query.filter(
                DiscountCoupon.valid_until < func.now()
            )
        elif status == "inactive":
            query = query.filter(DiscountCoupon.is_active == False)
    
    if campaign:
        query = query.filter(DiscountCoupon.campaign_name.ilike(f"%{campaign}%"))
    
    coupons = query.order_by(DiscountCoupon.created_at.desc()).all()
    
    coupons_data = []
    for coupon in coupons:
        coupons_data.append({
            "id": str(coupon.id),
            "coupon_code": coupon.coupon_code,
            "coupon_name": coupon.coupon_name,
            "description": coupon.description,
            "discount_type": coupon.discount_type.value,
            "discount_value": float(coupon.discount_value),
            "max_discount_amount": float(coupon.max_discount_amount) if coupon.max_discount_amount else None,
            "min_order_amount": float(coupon.min_order_amount) if coupon.min_order_amount else None,
            "usage_limits": {
                "total_usage_limit": coupon.total_usage_limit,
                "per_user_usage_limit": coupon.per_user_usage_limit,
                "current_usage_count": coupon.current_usage_count
            },
            "validity": {
                "valid_from": coupon.valid_from.isoformat(),
                "valid_until": coupon.valid_until.isoformat(),
                "is_active": coupon.is_active
            },
            "targeting": {
                "applicable_programs": coupon.applicable_programs,
                "applicable_categories": coupon.applicable_categories,
                "applicable_countries": coupon.applicable_countries,
                "first_time_users_only": coupon.first_time_users_only
            },
            "campaign_info": {
                "campaign_name": coupon.campaign_name,
                "campaign_source": coupon.campaign_source,
                "is_public": coupon.is_public,
                "is_auto_apply": coupon.is_auto_apply
            },
            "metadata": {
                "created_by": coupon.created_by,
                "created_at": coupon.created_at.isoformat()
            }
        })
    
    return {
        "status": "success",
        "data": {
            "coupons": coupons_data,
            "total_count": len(coupons_data),
            "filters": {
                "status": status,
                "campaign": campaign
            }
        }
    }


@router.put("/coupons/{coupon_id}")
async def update_discount_coupon(
    coupon_id: str,
    coupon_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Update discount coupon"""
    
    coupon = db.query(DiscountCoupon).filter(DiscountCoupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    # Update allowed fields
    updatable_fields = [
        'coupon_name', 'description', 'discount_value', 'max_discount_amount',
        'min_order_amount', 'total_usage_limit', 'per_user_usage_limit',
        'valid_until', 'is_active', 'applicable_programs', 'applicable_categories',
        'applicable_countries', 'first_time_users_only', 'is_public', 'is_auto_apply'
    ]
    
    for field in updatable_fields:
        if field in coupon_data:
            setattr(coupon, field, coupon_data[field])
    
    try:
        db.commit()
        return {
            "status": "success",
            "message": "Coupon updated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update coupon: {str(e)}"
        )


@router.delete("/coupons/{coupon_id}")
async def delete_discount_coupon(
    coupon_id: str,
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Delete discount coupon"""
    
    coupon = db.query(DiscountCoupon).filter(DiscountCoupon.id == coupon_id).first()
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    try:
        db.delete(coupon)
        db.commit()
        return {
            "status": "success",
            "message": "Coupon deleted successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete coupon: {str(e)}"
        )


@router.post("/programs")
async def create_certification_program(
    program_data: Dict[str, Any],
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Create new certification program"""
    
    try:
        program = CertificationProgram(
            program_code=program_data['program_code'],
            title=program_data['title'],
            description=program_data.get('description'),
            detailed_syllabus=program_data.get('detailed_syllabus'),
            
            # Classification
            category=program_data['category'],
            subcategory=program_data.get('subcategory'),
            level=program_data['level'],
            duration_hours=program_data.get('duration_hours'),
            validity_months=program_data.get('validity_months', 24),
            
            # Eligibility
            min_education_level=program_data.get('min_education_level'),
            min_age=program_data.get('min_age', 16),
            max_age=program_data.get('max_age'),
            prerequisites=program_data.get('prerequisites', []),
            target_audience=program_data.get('target_audience', []),
            
            # Pricing
            base_price=program_data['base_price'],
            discounted_price=program_data.get('discounted_price'),
            currency=program_data.get('currency', 'INR'),
            pricing_tiers=program_data.get('pricing_tiers', {}),
            
            # Exam configuration
            total_questions=program_data.get('total_questions', 100),
            exam_duration_minutes=program_data.get('exam_duration_minutes', 120),
            passing_percentage=program_data.get('passing_percentage', 70),
            max_attempts=program_data.get('max_attempts', 3),
            retake_fee=program_data.get('retake_fee'),
            
            # Content
            study_materials=program_data.get('study_materials', []),
            practice_tests_count=program_data.get('practice_tests_count', 5),
            video_lectures_hours=program_data.get('video_lectures_hours', 0),
            
            # Status
            is_featured=program_data.get('is_featured', False)
        )
        
        db.add(program)
        db.commit()
        
        return {
            "status": "success",
            "data": {
                "program_id": str(program.id),
                "program_code": program.program_code,
                "message": "Certification program created successfully"
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create program: {str(e)}"
        )


@router.get("/analytics")
async def get_pricing_analytics(
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Get pricing and revenue analytics"""
    
    analytics = pricing_management_service.get_pricing_analytics(db)
    
    return {
        "status": "success",
        "data": analytics
    }


@router.get("/revenue-report")
async def get_revenue_report(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_user: User = Depends(get_super_admin_user),
    db: Session = Depends(get_db)
):
    """Generate revenue report for specified period"""
    
    from datetime import datetime
    from app.models.independent_learner import IndependentPayment
    from sqlalchemy import func, and_
    
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Get payment data for the period
    payments = db.query(IndependentPayment).filter(
        and_(
            IndependentPayment.completed_at >= start_dt,
            IndependentPayment.completed_at <= end_dt,
            IndependentPayment.status == "success"
        )
    ).all()
    
    # Calculate metrics
    total_revenue = sum(float(p.amount) for p in payments)
    total_transactions = len(payments)
    
    # Payment method breakdown
    payment_methods = {}
    for payment in payments:
        method = payment.payment_method or "unknown"
        payment_methods[method] = payment_methods.get(method, 0) + float(payment.amount)
    
    # Payment type breakdown
    payment_types = {}
    for payment in payments:
        ptype = payment.payment_type or "unknown"
        payment_types[ptype] = payment_types.get(ptype, 0) + float(payment.amount)
    
    report_data = {
        "period": {
            "start_date": start_date,
            "end_date": end_date
        },
        "summary": {
            "total_revenue": total_revenue,
            "total_transactions": total_transactions,
            "average_transaction_value": round(total_revenue / total_transactions, 2) if total_transactions > 0 else 0
        },
        "breakdown": {
            "payment_methods": payment_methods,
            "payment_types": payment_types
        }
    }
    
    return {
        "status": "success",
        "data": report_data
    }
