"""
Independent Learner API routes for MEDHASAKTHI
For individuals registering outside of institutions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Any, Optional

from app.core.database import get_db
from app.api.v1.auth.dependencies import get_current_user
from app.models.user import User
from app.services.independent_learner_service import independent_learner_service

router = APIRouter()


@router.post("/register")
async def register_independent_learner(
    registration_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """Register a new independent learner"""
    
    success, message, data = await independent_learner_service.register_independent_learner(
        registration_data, db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "status": "success",
        "message": message,
        "data": data
    }


@router.get("/programs")
async def get_available_programs(
    category: Optional[str] = Query(None, description="Filter by program category"),
    level: Optional[str] = Query(None, description="Filter by difficulty level"),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available certification programs"""
    
    # Get learner ID if user is logged in
    learner_id = None
    if current_user and current_user.role == "independent_learner":
        from app.models.independent_learner import IndependentLearner
        learner = db.query(IndependentLearner).filter(
            IndependentLearner.user_id == current_user.id
        ).first()
        if learner:
            learner_id = learner.learner_id
    
    programs = independent_learner_service.get_available_programs(
        learner_id=learner_id,
        category=category,
        level=level,
        db=db
    )
    
    return {
        "status": "success",
        "data": {
            "programs": programs,
            "total_count": len(programs),
            "filters": {
                "category": category,
                "level": level
            }
        }
    }


@router.get("/programs/{program_id}/pricing")
async def get_program_pricing(
    program_id: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed pricing for a specific program"""
    
    # Get learner ID if user is logged in
    learner_id = None
    if current_user and current_user.role == "independent_learner":
        from app.models.independent_learner import IndependentLearner
        learner = db.query(IndependentLearner).filter(
            IndependentLearner.user_id == current_user.id
        ).first()
        if learner:
            learner_id = learner.learner_id
    
    pricing = independent_learner_service.calculate_program_pricing(
        program_id=program_id,
        learner_id=learner_id,
        db=db
    )
    
    return {
        "status": "success",
        "data": pricing
    }


@router.get("/dashboard")
async def get_learner_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for independent learner"""
    
    if current_user.role != "independent_learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Independent learner access required"
        )
    
    # Get learner profile
    from app.models.independent_learner import IndependentLearner
    learner = db.query(IndependentLearner).filter(
        IndependentLearner.user_id == current_user.id
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    
    dashboard_data = independent_learner_service.get_learner_dashboard(
        learner.learner_id, db
    )
    
    return {
        "status": "success",
        "data": dashboard_data
    }


@router.get("/profile")
async def get_learner_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learner's profile information"""
    
    if current_user.role != "independent_learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Independent learner access required"
        )
    
    from app.models.independent_learner import IndependentLearner
    learner = db.query(IndependentLearner).filter(
        IndependentLearner.user_id == current_user.id
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    
    profile_data = {
        "basic_info": {
            "learner_id": learner.learner_id,
            "first_name": learner.first_name,
            "last_name": learner.last_name,
            "email": learner.user.email,
            "phone": learner.phone,
            "alternate_phone": learner.alternate_phone,
            "date_of_birth": learner.date_of_birth.isoformat() if learner.date_of_birth else None,
            "gender": learner.gender,
            "nationality": learner.nationality
        },
        "address_info": {
            "address_line1": learner.address_line1,
            "address_line2": learner.address_line2,
            "city": learner.city,
            "state": learner.state,
            "country": learner.country,
            "postal_code": learner.postal_code
        },
        "professional_info": {
            "category": learner.category.value,
            "education_level": learner.education_level.value,
            "current_occupation": learner.current_occupation,
            "organization_name": learner.organization_name,
            "work_experience_years": learner.work_experience_years,
            "annual_income_range": learner.annual_income_range
        },
        "educational_background": {
            "highest_qualification": learner.highest_qualification,
            "specialization": learner.specialization,
            "university_college": learner.university_college,
            "graduation_year": learner.graduation_year,
            "percentage_cgpa": learner.percentage_cgpa
        },
        "learning_preferences": {
            "preferred_subjects": learner.preferred_subjects,
            "learning_goals": learner.learning_goals,
            "preferred_exam_types": learner.preferred_exam_types,
            "study_time_availability": learner.study_time_availability,
            "preferred_language": learner.preferred_language
        },
        "account_status": {
            "is_active": learner.is_active,
            "is_verified": learner.is_verified,
            "verification_level": learner.verification_level,
            "kyc_completed": learner.kyc_completed,
            "subscription_type": learner.subscription_type
        },
        "referral_info": {
            "referral_code": learner.referral_code,
            "referral_bonus_earned": float(learner.referral_bonus_earned),
            "referred_by_code": learner.referred_by_code
        }
    }
    
    return {
        "status": "success",
        "data": profile_data
    }


@router.put("/profile")
async def update_learner_profile(
    profile_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update learner's profile information"""
    
    if current_user.role != "independent_learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Independent learner access required"
        )
    
    from app.models.independent_learner import IndependentLearner
    learner = db.query(IndependentLearner).filter(
        IndependentLearner.user_id == current_user.id
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    
    # Update allowed fields
    updatable_fields = [
        'phone', 'alternate_phone', 'address_line1', 'address_line2',
        'city', 'state', 'country', 'postal_code', 'current_occupation',
        'organization_name', 'work_experience_years', 'annual_income_range',
        'highest_qualification', 'specialization', 'university_college',
        'graduation_year', 'percentage_cgpa', 'preferred_subjects',
        'learning_goals', 'preferred_exam_types', 'study_time_availability',
        'preferred_language'
    ]
    
    for field in updatable_fields:
        if field in profile_data:
            setattr(learner, field, profile_data[field])
    
    # Update user fields
    if 'first_name' in profile_data:
        learner.first_name = profile_data['first_name']
        learner.user.full_name = f"{profile_data['first_name']} {learner.last_name}"
    
    if 'last_name' in profile_data:
        learner.last_name = profile_data['last_name']
        learner.user.full_name = f"{learner.first_name} {profile_data['last_name']}"
    
    try:
        db.commit()
        return {
            "status": "success",
            "message": "Profile updated successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.get("/registrations")
async def get_exam_registrations(
    status: Optional[str] = Query(None, description="Filter by registration status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learner's exam registrations"""
    
    if current_user.role != "independent_learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Independent learner access required"
        )
    
    from app.models.independent_learner import IndependentLearner, IndependentExamRegistration
    learner = db.query(IndependentLearner).filter(
        IndependentLearner.user_id == current_user.id
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    
    query = db.query(IndependentExamRegistration).filter(
        IndependentExamRegistration.learner_id == learner.id
    )
    
    if status:
        query = query.filter(IndependentExamRegistration.status == status)
    
    registrations = query.order_by(
        IndependentExamRegistration.created_at.desc()
    ).all()
    
    registrations_data = []
    for reg in registrations:
        registrations_data.append({
            "id": str(reg.id),
            "registration_number": reg.registration_number,
            "program": {
                "id": str(reg.program.id),
                "title": reg.program.title,
                "code": reg.program.program_code,
                "category": reg.program.category
            },
            "registration_date": reg.registration_date.isoformat(),
            "exam_date": reg.exam_date.isoformat() if reg.exam_date else None,
            "exam_time": reg.exam_time,
            "exam_center": reg.exam_center,
            "amount_paid": float(reg.amount_paid),
            "payment_status": reg.payment_status,
            "status": reg.status,
            "attempt_number": reg.attempt_number,
            "score_obtained": reg.score_obtained,
            "percentage": float(reg.percentage) if reg.percentage else None,
            "result": reg.result,
            "grade": reg.grade
        })
    
    return {
        "status": "success",
        "data": {
            "registrations": registrations_data,
            "total_count": len(registrations_data),
            "filter": {
                "status": status
            }
        }
    }


@router.get("/certificates")
async def get_certificates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learner's certificates"""
    
    if current_user.role != "independent_learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Independent learner access required"
        )
    
    from app.models.independent_learner import IndependentLearner, IndependentCertificate
    learner = db.query(IndependentLearner).filter(
        IndependentLearner.user_id == current_user.id
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    
    certificates = db.query(IndependentCertificate).filter(
        IndependentCertificate.learner_id == learner.id
    ).order_by(IndependentCertificate.issue_date.desc()).all()
    
    certificates_data = []
    for cert in certificates:
        certificates_data.append({
            "id": str(cert.id),
            "certificate_number": cert.certificate_number,
            "program": {
                "title": cert.program_title,
                "code": cert.program.program_code
            },
            "issue_date": cert.issue_date.isoformat(),
            "expiry_date": cert.expiry_date.isoformat() if cert.expiry_date else None,
            "score_achieved": cert.score_achieved,
            "grade_obtained": cert.grade_obtained,
            "verification_code": cert.verification_code,
            "certificate_url": cert.certificate_url,
            "status": cert.status,
            "is_verified": cert.is_verified
        })
    
    return {
        "status": "success",
        "data": {
            "certificates": certificates_data,
            "total_count": len(certificates_data)
        }
    }


@router.get("/referrals")
async def get_referral_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get learner's referral information and earnings"""
    
    if current_user.role != "independent_learner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Independent learner access required"
        )
    
    from app.models.independent_learner import IndependentLearner
    learner = db.query(IndependentLearner).filter(
        IndependentLearner.user_id == current_user.id
    ).first()
    
    if not learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    
    # Count successful referrals
    successful_referrals = db.query(IndependentLearner).filter(
        IndependentLearner.referred_by_code == learner.referral_code,
        IndependentLearner.is_active == True
    ).count()
    
    return {
        "status": "success",
        "data": {
            "referral_code": learner.referral_code,
            "total_referrals": successful_referrals,
            "total_bonus_earned": float(learner.referral_bonus_earned),
            "referral_link": f"https://medhasakthi.com/register?ref={learner.referral_code}",
            "bonus_per_referral": 100.00,  # Configure this
            "terms": "Earn ₹100 for each successful referral who completes their first certification"
        }
    }
