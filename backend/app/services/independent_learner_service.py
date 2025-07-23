"""
Independent Learner Service for MEDHASAKTHI
Handles registration, pricing, and certification for individual learners
"""
import uuid
import random
import string
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from fastapi import HTTPException, status
from datetime import datetime, timedelta, date
from decimal import Decimal

from app.models.user import User
from app.models.independent_learner import (
    IndependentLearner, CertificationProgram, IndependentExamRegistration,
    IndependentCertificate, IndependentPayment, LearnerCategory, EducationLevel
)
from app.models.pricing_config import (
    GlobalPricingConfig, ProgramPricingOverride, DiscountCoupon, CouponUsage
)
from app.core.security import get_password_hash
from app.services.email_service import email_service


class IndependentLearnerService:
    """Service for independent learner operations"""
    
    def __init__(self):
        self.learner_id_prefix = "IL"  # Independent Learner prefix
        self.registration_prefix = "REG"
        self.certificate_prefix = "CERT"
    
    def generate_learner_id(self, db: Session) -> str:
        """Generate unique learner ID"""
        while True:
            # Generate ID: IL + YYYYMM + 6-digit random number
            year_month = datetime.now().strftime("%Y%m")
            random_digits = ''.join(random.choices(string.digits, k=6))
            learner_id = f"{self.learner_id_prefix}{year_month}{random_digits}"
            
            # Check if ID already exists
            existing = db.query(IndependentLearner).filter(
                IndependentLearner.learner_id == learner_id
            ).first()
            
            if not existing:
                return learner_id
    
    def generate_referral_code(self, first_name: str, last_name: str) -> str:
        """Generate referral code for learner"""
        # Take first 3 letters of first name and last name + 4 random digits
        first_part = first_name[:3].upper()
        last_part = last_name[:3].upper()
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"{first_part}{last_part}{random_part}"
    
    async def register_independent_learner(
        self,
        registration_data: Dict[str, Any],
        db: Session
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Register a new independent learner"""
        
        try:
            # Validate required fields
            required_fields = [
                'email', 'password', 'first_name', 'last_name', 'phone',
                'category', 'education_level', 'date_of_birth'
            ]
            
            for field in required_fields:
                if field not in registration_data or not registration_data[field]:
                    return False, f"Missing required field: {field}", None
            
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == registration_data['email']).first()
            if existing_user:
                return False, "Email already registered", None
            
            # Generate learner ID and referral code
            learner_id = self.generate_learner_id(db)
            referral_code = self.generate_referral_code(
                registration_data['first_name'],
                registration_data['last_name']
            )
            
            # Create User account
            user = User(
                email=registration_data['email'],
                full_name=f"{registration_data['first_name']} {registration_data['last_name']}",
                password_hash=get_password_hash(registration_data['password']),
                role="independent_learner",
                is_active=True,
                is_email_verified=False  # Require email verification
            )
            
            db.add(user)
            db.flush()  # Get user ID
            
            # Create Independent Learner profile
            learner = IndependentLearner(
                user_id=user.id,
                learner_id=learner_id,
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                phone=registration_data['phone'],
                category=LearnerCategory(registration_data['category']),
                education_level=EducationLevel(registration_data['education_level']),
                referral_code=referral_code,
                date_of_birth=datetime.strptime(registration_data['date_of_birth'], '%Y-%m-%d').date(),
                
                # Optional fields
                alternate_phone=registration_data.get('alternate_phone'),
                address_line1=registration_data.get('address_line1'),
                address_line2=registration_data.get('address_line2'),
                city=registration_data.get('city'),
                state=registration_data.get('state'),
                country=registration_data.get('country', 'India'),
                postal_code=registration_data.get('postal_code'),
                gender=registration_data.get('gender'),
                nationality=registration_data.get('nationality', 'Indian'),
                
                # Professional information
                current_occupation=registration_data.get('current_occupation'),
                organization_name=registration_data.get('organization_name'),
                work_experience_years=registration_data.get('work_experience_years', 0),
                annual_income_range=registration_data.get('annual_income_range'),
                
                # Educational background
                highest_qualification=registration_data.get('highest_qualification'),
                specialization=registration_data.get('specialization'),
                university_college=registration_data.get('university_college'),
                graduation_year=registration_data.get('graduation_year'),
                percentage_cgpa=registration_data.get('percentage_cgpa'),
                
                # Learning preferences
                preferred_subjects=registration_data.get('preferred_subjects', []),
                learning_goals=registration_data.get('learning_goals'),
                preferred_exam_types=registration_data.get('preferred_exam_types', []),
                study_time_availability=registration_data.get('study_time_availability'),
                preferred_language=registration_data.get('preferred_language', 'English'),
                
                # Handle referral
                referred_by_code=registration_data.get('referred_by_code')
            )
            
            db.add(learner)
            db.commit()
            
            # Send verification email
            await self._send_verification_email(user, learner)
            
            # Process referral bonus if applicable
            if registration_data.get('referred_by_code'):
                await self._process_referral_bonus(registration_data['referred_by_code'], learner.id, db)
            
            return True, "Registration successful. Please verify your email.", {
                "learner_id": learner_id,
                "user_id": str(user.id),
                "referral_code": referral_code
            }
            
        except Exception as e:
            db.rollback()
            return False, f"Registration failed: {str(e)}", None
    
    async def _send_verification_email(self, user: User, learner: IndependentLearner):
        """Send email verification to new learner"""
        
        verification_token = str(uuid.uuid4())
        # Store verification token in user record (you might want to add this field)
        
        email_content = f"""
        Dear {learner.first_name},

        Welcome to MEDHASAKTHI! Your independent learner account has been created.

        Account Details:
        Learner ID: {learner.learner_id}
        Email: {user.email}
        Referral Code: {learner.referral_code}

        Please verify your email by clicking the link below:
        https://medhasakthi.com/verify-email?token={verification_token}

        Start your certification journey today!

        Best regards,
        MEDHASAKTHI Team
        """
        
        try:
            email_service.send_email(
                to_email=user.email,
                subject="Welcome to MEDHASAKTHI - Verify Your Email",
                content=email_content
            )
        except Exception as e:
            print(f"Failed to send verification email: {str(e)}")
    
    async def _process_referral_bonus(self, referral_code: str, new_learner_id: str, db: Session):
        """Process referral bonus for both referrer and referee"""
        
        try:
            # Find the referrer
            referrer = db.query(IndependentLearner).filter(
                IndependentLearner.referral_code == referral_code
            ).first()
            
            if referrer:
                # Add referral bonus (you can configure this amount)
                bonus_amount = Decimal('100.00')  # ₹100 bonus
                referrer.referral_bonus_earned += bonus_amount
                
                # You might want to create a referral bonus record here
                db.commit()
                
                # Send notification emails to both parties
                await self._send_referral_bonus_notification(referrer, new_learner_id, bonus_amount)
                
        except Exception as e:
            print(f"Failed to process referral bonus: {str(e)}")
    
    async def _send_referral_bonus_notification(self, referrer: IndependentLearner, new_learner_id: str, bonus_amount: Decimal):
        """Send referral bonus notification"""
        
        email_content = f"""
        Dear {referrer.first_name},

        Great news! You've earned a referral bonus of ₹{bonus_amount} for referring a new learner.

        Your total referral earnings: ₹{referrer.referral_bonus_earned}

        Keep sharing your referral code: {referrer.referral_code}

        Best regards,
        MEDHASAKTHI Team
        """
        
        try:
            email_service.send_email(
                to_email=referrer.user.email,
                subject="Referral Bonus Earned - MEDHASAKTHI",
                content=email_content
            )
        except Exception as e:
            print(f"Failed to send referral bonus notification: {str(e)}")
    
    def get_available_programs(
        self,
        learner_id: Optional[str] = None,
        category: Optional[str] = None,
        level: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Get available certification programs for independent learners"""
        
        query = db.query(CertificationProgram).filter(
            CertificationProgram.is_active == True
        )
        
        # Apply filters
        if category:
            query = query.filter(CertificationProgram.category == category)
        if level:
            query = query.filter(CertificationProgram.level == level)
        
        programs = query.order_by(CertificationProgram.is_featured.desc()).all()
        
        programs_data = []
        for program in programs:
            # Calculate pricing for the learner
            pricing = self.calculate_program_pricing(program.id, learner_id, db)
            
            programs_data.append({
                "id": str(program.id),
                "program_code": program.program_code,
                "title": program.title,
                "description": program.description,
                "category": program.category,
                "subcategory": program.subcategory,
                "level": program.level,
                "duration_hours": program.duration_hours,
                "validity_months": program.validity_months,
                "pricing": pricing,
                "exam_config": {
                    "total_questions": program.total_questions,
                    "duration_minutes": program.exam_duration_minutes,
                    "passing_percentage": program.passing_percentage,
                    "max_attempts": program.max_attempts
                },
                "statistics": {
                    "total_enrollments": program.total_enrollments,
                    "success_rate": float(program.success_rate) if program.success_rate else 0,
                    "average_score": float(program.average_score) if program.average_score else 0
                },
                "is_featured": program.is_featured,
                "enrollment_open": (
                    program.enrollment_start_date <= date.today() <= program.enrollment_end_date
                    if program.enrollment_start_date and program.enrollment_end_date
                    else True
                )
            })
        
        return programs_data
    
    def calculate_program_pricing(
        self,
        program_id: str,
        learner_id: Optional[str] = None,
        db: Session = None
    ) -> Dict[str, Any]:
        """Calculate pricing for a program based on learner category and current offers"""
        
        # Get program details
        program = db.query(CertificationProgram).filter(
            CertificationProgram.id == program_id
        ).first()
        
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Program not found"
            )
        
        # Get global pricing config
        global_config = db.query(GlobalPricingConfig).filter(
            GlobalPricingConfig.is_active == True,
            GlobalPricingConfig.approval_status == "active"
        ).order_by(GlobalPricingConfig.created_at.desc()).first()
        
        if not global_config:
            # Fallback to program base price
            return {
                "base_price": float(program.base_price),
                "final_price": float(program.base_price),
                "currency": program.currency,
                "discounts": [],
                "total_discount": 0
            }
        
        # Start with program base price or global base price
        base_price = program.base_price or global_config.base_exam_fee
        
        # Get learner category for pricing
        learner_multiplier = 1.0
        learner_category = None
        
        if learner_id:
            learner = db.query(IndependentLearner).filter(
                IndependentLearner.learner_id == learner_id
            ).first()
            
            if learner:
                learner_category = learner.category
                
                # Apply category-based multiplier
                if learner.category == LearnerCategory.SCHOOL_STUDENT:
                    learner_multiplier = float(global_config.student_multiplier)
                elif learner.category == LearnerCategory.WORKING_PROFESSIONAL:
                    learner_multiplier = float(global_config.professional_multiplier)
                # Add more category mappings as needed
        
        # Calculate category-adjusted price
        category_price = base_price * Decimal(str(learner_multiplier))
        
        # Check for program-specific overrides
        program_override = db.query(ProgramPricingOverride).filter(
            ProgramPricingOverride.program_id == program_id,
            ProgramPricingOverride.is_active == True,
            ProgramPricingOverride.valid_from <= datetime.utcnow(),
            or_(
                ProgramPricingOverride.valid_until.is_(None),
                ProgramPricingOverride.valid_until >= datetime.utcnow()
            )
        ).first()
        
        if program_override and program_override.custom_base_price:
            category_price = program_override.custom_base_price
        
        # Apply available discounts
        discounts = []
        total_discount = Decimal('0')
        
        # Check for applicable coupons
        applicable_coupons = db.query(DiscountCoupon).filter(
            DiscountCoupon.is_active == True,
            DiscountCoupon.valid_from <= datetime.utcnow(),
            DiscountCoupon.valid_until >= datetime.utcnow(),
            DiscountCoupon.is_auto_apply == True
        ).all()
        
        for coupon in applicable_coupons:
            # Check if coupon is applicable to this program/category
            if self._is_coupon_applicable(coupon, program, learner_category):
                discount_amount = self._calculate_coupon_discount(coupon, category_price)
                if discount_amount > 0:
                    discounts.append({
                        "type": "coupon",
                        "code": coupon.coupon_code,
                        "name": coupon.coupon_name,
                        "amount": float(discount_amount)
                    })
                    total_discount += discount_amount
        
        # Calculate final price
        final_price = max(category_price - total_discount, Decimal('0'))
        
        return {
            "base_price": float(base_price),
            "category_price": float(category_price),
            "final_price": float(final_price),
            "currency": program.currency,
            "learner_category": learner_category.value if learner_category else None,
            "category_multiplier": learner_multiplier,
            "discounts": discounts,
            "total_discount": float(total_discount),
            "retake_fee": float(program.retake_fee) if program.retake_fee else float(global_config.base_retake_fee)
        }
    
    def _is_coupon_applicable(self, coupon: DiscountCoupon, program: CertificationProgram, learner_category: Optional[LearnerCategory]) -> bool:
        """Check if coupon is applicable to program and learner"""
        
        # Check program applicability
        if coupon.applicable_programs:
            if str(program.id) not in coupon.applicable_programs:
                return False
        
        # Check category applicability
        if coupon.applicable_categories and learner_category:
            if learner_category.value not in coupon.applicable_categories:
                return False
        
        # Check usage limits
        if coupon.total_usage_limit and coupon.current_usage_count >= coupon.total_usage_limit:
            return False
        
        return True
    
    def _calculate_coupon_discount(self, coupon: DiscountCoupon, price: Decimal) -> Decimal:
        """Calculate discount amount from coupon"""
        
        if coupon.min_order_amount and price < coupon.min_order_amount:
            return Decimal('0')
        
        if coupon.discount_type == "percentage":
            discount = price * (coupon.discount_value / 100)
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)
            return discount
        elif coupon.discount_type == "fixed_amount":
            return min(coupon.discount_value, price)
        
        return Decimal('0')
    
    def get_learner_dashboard(self, learner_id: str, db: Session) -> Dict[str, Any]:
        """Get dashboard data for independent learner"""
        
        learner = db.query(IndependentLearner).filter(
            IndependentLearner.learner_id == learner_id
        ).first()
        
        if not learner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Learner not found"
            )
        
        # Get registration statistics
        total_registrations = db.query(IndependentExamRegistration).filter(
            IndependentExamRegistration.learner_id == learner.id
        ).count()
        
        completed_exams = db.query(IndependentExamRegistration).filter(
            IndependentExamRegistration.learner_id == learner.id,
            IndependentExamRegistration.status.in_(["passed", "failed"])
        ).count()
        
        certificates_earned = db.query(IndependentCertificate).filter(
            IndependentCertificate.learner_id == learner.id,
            IndependentCertificate.status == "active"
        ).count()
        
        # Get recent activities
        recent_registrations = db.query(IndependentExamRegistration).filter(
            IndependentExamRegistration.learner_id == learner.id
        ).order_by(IndependentExamRegistration.created_at.desc()).limit(5).all()
        
        # Get upcoming exams
        upcoming_exams = db.query(IndependentExamRegistration).filter(
            IndependentExamRegistration.learner_id == learner.id,
            IndependentExamRegistration.exam_date >= date.today(),
            IndependentExamRegistration.status == "registered"
        ).order_by(IndependentExamRegistration.exam_date).all()
        
        return {
            "learner_info": {
                "learner_id": learner.learner_id,
                "name": f"{learner.first_name} {learner.last_name}",
                "email": learner.user.email,
                "category": learner.category.value,
                "education_level": learner.education_level.value,
                "verification_level": learner.verification_level,
                "subscription_type": learner.subscription_type,
                "referral_code": learner.referral_code,
                "referral_bonus": float(learner.referral_bonus_earned)
            },
            "statistics": {
                "total_registrations": total_registrations,
                "completed_exams": completed_exams,
                "certificates_earned": certificates_earned,
                "success_rate": round((certificates_earned / completed_exams * 100) if completed_exams > 0 else 0, 2)
            },
            "recent_activities": [
                {
                    "type": "exam_registration",
                    "program_title": reg.program.title,
                    "registration_date": reg.registration_date.isoformat(),
                    "exam_date": reg.exam_date.isoformat() if reg.exam_date else None,
                    "status": reg.status
                }
                for reg in recent_registrations
            ],
            "upcoming_exams": [
                {
                    "registration_id": str(exam.id),
                    "program_title": exam.program.title,
                    "exam_date": exam.exam_date.isoformat(),
                    "exam_time": exam.exam_time,
                    "status": exam.status
                }
                for exam in upcoming_exams
            ]
        }


# Global instance
independent_learner_service = IndependentLearnerService()


class PricingManagementService:
    """Service for super admin pricing management"""

    def create_global_pricing_config(
        self,
        config_data: Dict[str, Any],
        admin_user: str,
        db: Session
    ) -> Dict[str, Any]:
        """Create new global pricing configuration"""

        try:
            # Deactivate current active config
            current_config = db.query(GlobalPricingConfig).filter(
                GlobalPricingConfig.is_active == True,
                GlobalPricingConfig.approval_status == "active"
            ).first()

            if current_config:
                current_config.is_active = False
                current_config.effective_until = datetime.utcnow()

            # Create new config
            new_config = GlobalPricingConfig(
                config_name=config_data['config_name'],
                config_version=config_data.get('config_version', '1.0'),
                description=config_data.get('description'),

                # Base pricing
                base_exam_fee=Decimal(str(config_data['base_exam_fee'])),
                base_certification_fee=Decimal(str(config_data['base_certification_fee'])),
                base_retake_fee=Decimal(str(config_data['base_retake_fee'])),

                # Currency
                primary_currency=config_data.get('primary_currency', 'INR'),
                supported_currencies=config_data.get('supported_currencies', ['INR']),
                currency_conversion_rates=config_data.get('currency_conversion_rates', {}),

                # Category multipliers
                student_multiplier=Decimal(str(config_data.get('student_multiplier', 0.7))),
                professional_multiplier=Decimal(str(config_data.get('professional_multiplier', 1.0))),
                enterprise_multiplier=Decimal(str(config_data.get('enterprise_multiplier', 1.2))),
                premium_multiplier=Decimal(str(config_data.get('premium_multiplier', 1.5))),

                # Geographic pricing
                country_pricing_multipliers=config_data.get('country_pricing_multipliers', {}),
                state_pricing_multipliers=config_data.get('state_pricing_multipliers', {}),
                city_tier_multipliers=config_data.get('city_tier_multipliers', {}),

                # Discounts
                bulk_discount_config=config_data.get('bulk_discount_config', {}),
                referral_discount_percent=config_data.get('referral_discount_percent', 10),
                loyalty_discount_config=config_data.get('loyalty_discount_config', {}),

                # Other configurations
                gateway_charges_config=config_data.get('gateway_charges_config', {}),
                convenience_fee_percent=Decimal(str(config_data.get('convenience_fee_percent', 2.0))),
                tax_config=config_data.get('tax_config', {}),
                tax_inclusive_pricing=config_data.get('tax_inclusive_pricing', True),

                # Metadata
                effective_from=datetime.utcnow(),
                created_by=admin_user,
                approval_status="active",
                approved_by=admin_user,
                approval_date=datetime.utcnow()
            )

            db.add(new_config)
            db.commit()

            return {
                "success": True,
                "config_id": str(new_config.id),
                "message": "Global pricing configuration created successfully"
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create pricing configuration: {str(e)}"
            )

    def create_discount_coupon(
        self,
        coupon_data: Dict[str, Any],
        admin_user: str,
        db: Session
    ) -> Dict[str, Any]:
        """Create new discount coupon"""

        try:
            # Check if coupon code already exists
            existing_coupon = db.query(DiscountCoupon).filter(
                DiscountCoupon.coupon_code == coupon_data['coupon_code']
            ).first()

            if existing_coupon:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Coupon code already exists"
                )

            coupon = DiscountCoupon(
                coupon_code=coupon_data['coupon_code'].upper(),
                coupon_name=coupon_data['coupon_name'],
                description=coupon_data.get('description'),

                # Discount configuration
                discount_type=coupon_data['discount_type'],
                discount_value=Decimal(str(coupon_data['discount_value'])),
                max_discount_amount=Decimal(str(coupon_data['max_discount_amount'])) if coupon_data.get('max_discount_amount') else None,
                min_order_amount=Decimal(str(coupon_data['min_order_amount'])) if coupon_data.get('min_order_amount') else None,

                # Usage limits
                total_usage_limit=coupon_data.get('total_usage_limit'),
                per_user_usage_limit=coupon_data.get('per_user_usage_limit', 1),

                # Validity
                valid_from=datetime.fromisoformat(coupon_data['valid_from']),
                valid_until=datetime.fromisoformat(coupon_data['valid_until']),

                # Targeting
                applicable_programs=coupon_data.get('applicable_programs', []),
                applicable_categories=coupon_data.get('applicable_categories', []),
                applicable_countries=coupon_data.get('applicable_countries', []),
                first_time_users_only=coupon_data.get('first_time_users_only', False),

                # Configuration
                is_public=coupon_data.get('is_public', False),
                is_auto_apply=coupon_data.get('is_auto_apply', False),

                # Campaign
                campaign_name=coupon_data.get('campaign_name'),
                campaign_source=coupon_data.get('campaign_source'),

                # Approval
                created_by=admin_user,
                approved_by=admin_user,
                approval_status="active"
            )

            db.add(coupon)
            db.commit()

            return {
                "success": True,
                "coupon_id": str(coupon.id),
                "coupon_code": coupon.coupon_code,
                "message": "Discount coupon created successfully"
            }

        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create discount coupon: {str(e)}"
            )

    def get_pricing_analytics(self, db: Session) -> Dict[str, Any]:
        """Get pricing and revenue analytics for super admin"""

        # Get current pricing config
        current_config = db.query(GlobalPricingConfig).filter(
            GlobalPricingConfig.is_active == True,
            GlobalPricingConfig.approval_status == "active"
        ).first()

        # Get total revenue (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        total_revenue = db.query(func.sum(IndependentPayment.amount)).filter(
            IndependentPayment.status == "success",
            IndependentPayment.completed_at >= thirty_days_ago
        ).scalar() or 0

        # Get registration statistics
        total_learners = db.query(IndependentLearner).count()
        active_learners = db.query(IndependentLearner).filter(
            IndependentLearner.is_active == True
        ).count()

        # Get program statistics
        total_programs = db.query(CertificationProgram).filter(
            CertificationProgram.is_active == True
        ).count()

        # Get coupon usage statistics
        active_coupons = db.query(DiscountCoupon).filter(
            DiscountCoupon.is_active == True,
            DiscountCoupon.valid_until >= datetime.utcnow()
        ).count()

        return {
            "current_config": {
                "config_name": current_config.config_name if current_config else None,
                "version": current_config.config_version if current_config else None,
                "effective_from": current_config.effective_from.isoformat() if current_config else None
            },
            "revenue_metrics": {
                "total_revenue_30_days": float(total_revenue),
                "currency": current_config.primary_currency if current_config else "INR"
            },
            "learner_metrics": {
                "total_learners": total_learners,
                "active_learners": active_learners,
                "activation_rate": round((active_learners / total_learners * 100) if total_learners > 0 else 0, 2)
            },
            "program_metrics": {
                "total_programs": total_programs,
                "active_coupons": active_coupons
            }
        }


# Global instance
pricing_management_service = PricingManagementService()
