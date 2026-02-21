"""
Pricing Configuration Models for MEDHASAKTHI
Super admin configurable pricing for independent learners
"""
import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, Text, JSON, Enum as SQLEnum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base


class PricingTier(str, Enum):
    """Pricing tiers for different user categories"""
    STUDENT = "student"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class DiscountType(str, Enum):
    """Types of discounts available"""
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    BUY_ONE_GET_ONE = "bogo"
    BULK_DISCOUNT = "bulk_discount"


class GlobalPricingConfig(Base):
    """Global pricing configuration managed by super admin"""
    __tablename__ = "global_pricing_config"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Configuration Information
    config_name = Column(String(100), nullable=False)
    config_version = Column(String(20), default="1.0")
    description = Column(Text)
    
    # Base Pricing Structure
    base_exam_fee = Column(Numeric(10, 2), nullable=False, default=500.00)
    base_certification_fee = Column(Numeric(10, 2), nullable=False, default=1000.00)
    base_retake_fee = Column(Numeric(10, 2), nullable=False, default=300.00)
    
    # Currency Configuration
    primary_currency = Column(String(10), default="INR")
    supported_currencies = Column(JSON)  # ["INR", "USD", "EUR"]
    currency_conversion_rates = Column(JSON)  # Exchange rates
    
    # Category-based Pricing Multipliers
    student_multiplier = Column(Numeric(5, 2), default=0.7)  # 30% discount for students
    professional_multiplier = Column(Numeric(5, 2), default=1.0)  # No discount
    enterprise_multiplier = Column(Numeric(5, 2), default=1.2)  # 20% premium
    premium_multiplier = Column(Numeric(5, 2), default=1.5)  # 50% premium
    
    # Geographic Pricing
    country_pricing_multipliers = Column(JSON)  # Country-specific pricing
    state_pricing_multipliers = Column(JSON)  # State-specific pricing (for India)
    city_tier_multipliers = Column(JSON)  # Tier 1, 2, 3 city pricing
    
    # Volume Discounts
    bulk_discount_config = Column(JSON)  # Bulk purchase discounts
    referral_discount_percent = Column(Integer, default=10)
    loyalty_discount_config = Column(JSON)  # Loyalty program discounts
    
    # Seasonal Pricing
    seasonal_discounts = Column(JSON)  # Festival/seasonal discounts
    promotional_campaigns = Column(JSON)  # Active promotional campaigns
    
    # Payment Gateway Charges
    gateway_charges_config = Column(JSON)  # Payment gateway specific charges
    convenience_fee_percent = Column(Numeric(5, 2), default=2.0)
    
    # Tax Configuration
    tax_config = Column(JSON)  # GST/VAT configuration by region
    tax_inclusive_pricing = Column(Boolean, default=True)
    
    # Status and Validity
    is_active = Column(Boolean, default=True)
    effective_from = Column(DateTime(timezone=True), nullable=False)
    effective_until = Column(DateTime(timezone=True))
    
    # Approval Workflow
    created_by = Column(String(100))  # Super admin who created
    approved_by = Column(String(100))  # Super admin who approved
    approval_status = Column(String(20), default="draft")  # draft, approved, active, archived
    approval_date = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<GlobalPricingConfig {self.config_name} v{self.config_version}>"


class ProgramPricingOverride(Base):
    """Program-specific pricing overrides"""
    __tablename__ = "program_pricing_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    program_id = Column(UUID(as_uuid=True), nullable=False)  # References certification_programs
    
    # Override Information
    override_name = Column(String(100), nullable=False)
    override_reason = Column(Text)
    
    # Pricing Overrides
    custom_base_price = Column(Numeric(10, 2))
    custom_retake_fee = Column(Numeric(10, 2))
    
    # Category-specific Overrides
    student_price_override = Column(Numeric(10, 2))
    professional_price_override = Column(Numeric(10, 2))
    enterprise_price_override = Column(Numeric(10, 2))
    premium_price_override = Column(Numeric(10, 2))
    
    # Special Pricing Rules
    early_bird_discount = Column(JSON)  # Early registration discounts
    group_discount_config = Column(JSON)  # Group registration discounts
    corporate_pricing = Column(JSON)  # Corporate bulk pricing
    
    # Geographic Overrides
    country_specific_pricing = Column(JSON)
    region_specific_pricing = Column(JSON)
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Approval
    created_by = Column(String(100))
    approved_by = Column(String(100))
    approval_status = Column(String(20), default="draft")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<ProgramPricingOverride {self.override_name}>"


class DiscountCoupon(Base):
    """Discount coupons for independent learners"""
    __tablename__ = "discount_coupons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Coupon Information
    coupon_code = Column(String(50), unique=True, nullable=False, index=True)
    coupon_name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Discount Configuration
    discount_type = Column(SQLEnum(DiscountType), nullable=False)
    discount_value = Column(Numeric(10, 2), nullable=False)  # Percentage or amount
    max_discount_amount = Column(Numeric(10, 2))  # Cap for percentage discounts
    min_order_amount = Column(Numeric(10, 2))  # Minimum order for coupon
    
    # Usage Limits
    total_usage_limit = Column(Integer)  # Total times coupon can be used
    per_user_usage_limit = Column(Integer, default=1)  # Times per user
    current_usage_count = Column(Integer, default=0)
    
    # Validity
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Targeting
    applicable_programs = Column(JSON)  # Specific programs
    applicable_categories = Column(JSON)  # Learner categories
    applicable_countries = Column(JSON)  # Geographic targeting
    first_time_users_only = Column(Boolean, default=False)
    
    # Coupon Type
    is_public = Column(Boolean, default=False)  # Public or private coupon
    is_auto_apply = Column(Boolean, default=False)  # Auto-apply for eligible users
    
    # Campaign Information
    campaign_name = Column(String(100))
    campaign_source = Column(String(100))  # email, social, affiliate, etc.
    
    # Approval
    created_by = Column(String(100))
    approved_by = Column(String(100))
    approval_status = Column(String(20), default="draft")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<DiscountCoupon {self.coupon_code}>"


class CouponUsage(Base):
    """Track coupon usage by learners"""
    __tablename__ = "coupon_usage"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    coupon_id = Column(UUID(as_uuid=True), nullable=False)
    learner_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Usage Information
    order_amount = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=False)
    final_amount = Column(Numeric(10, 2), nullable=False)
    
    # Transaction Details
    payment_id = Column(String(100))
    registration_id = Column(UUID(as_uuid=True))
    
    # Usage Context
    usage_source = Column(String(50))  # web, mobile, api
    user_agent = Column(String(500))
    ip_address = Column(String(50))
    
    # Timestamps
    used_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CouponUsage {self.coupon_id} by {self.learner_id}>"


class PricingAuditLog(Base):
    """Audit log for pricing changes"""
    __tablename__ = "pricing_audit_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Change Information
    entity_type = Column(String(50), nullable=False)  # global_config, program_override, coupon
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String(50), nullable=False)  # create, update, delete, activate, deactivate
    
    # Change Details
    field_changed = Column(String(100))
    old_value = Column(Text)
    new_value = Column(Text)
    change_reason = Column(Text)
    
    # User Information
    changed_by = Column(String(100), nullable=False)
    user_role = Column(String(50))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Impact Analysis
    affected_programs = Column(JSON)  # Programs affected by change
    estimated_revenue_impact = Column(Numeric(15, 2))
    affected_learners_count = Column(Integer)
    
    # Timestamps
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<PricingAuditLog {self.action} on {self.entity_type}>"


class RevenueReport(Base):
    """Revenue reporting and analytics"""
    __tablename__ = "revenue_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Report Information
    report_name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    report_period_start = Column(Date, nullable=False)
    report_period_end = Column(Date, nullable=False)
    
    # Revenue Metrics
    total_revenue = Column(Numeric(15, 2), default=0)
    exam_fee_revenue = Column(Numeric(15, 2), default=0)
    certification_revenue = Column(Numeric(15, 2), default=0)
    retake_fee_revenue = Column(Numeric(15, 2), default=0)
    
    # Discount Impact
    total_discounts_given = Column(Numeric(15, 2), default=0)
    coupon_discounts = Column(Numeric(15, 2), default=0)
    bulk_discounts = Column(Numeric(15, 2), default=0)
    referral_discounts = Column(Numeric(15, 2), default=0)
    
    # Volume Metrics
    total_registrations = Column(Integer, default=0)
    total_certifications = Column(Integer, default=0)
    total_retakes = Column(Integer, default=0)
    
    # Category Breakdown
    student_revenue = Column(Numeric(15, 2), default=0)
    professional_revenue = Column(Numeric(15, 2), default=0)
    enterprise_revenue = Column(Numeric(15, 2), default=0)
    
    # Geographic Breakdown
    country_wise_revenue = Column(JSON)
    state_wise_revenue = Column(JSON)
    city_wise_revenue = Column(JSON)
    
    # Program Performance
    top_performing_programs = Column(JSON)
    program_wise_revenue = Column(JSON)
    
    # Payment Analytics
    payment_method_breakdown = Column(JSON)
    gateway_wise_revenue = Column(JSON)
    refund_amount = Column(Numeric(15, 2), default=0)
    
    # Report Status
    status = Column(String(20), default="generated")  # generated, reviewed, published
    generated_by = Column(String(100))
    reviewed_by = Column(String(100))
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<RevenueReport {self.report_name} for {self.report_period_start} to {self.report_period_end}>"
