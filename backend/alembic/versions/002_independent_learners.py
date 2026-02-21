"""Add independent learners and pricing models

Revision ID: 002_independent_learners
Revises: 001_initial_schema
Create Date: 2024-01-20 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_independent_learners'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create independent_learners table
    op.create_table('independent_learners',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('learner_id', sa.String(length=50), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.Enum('male', 'female', 'other', 'prefer_not_to_say', name='gender'), nullable=True),
        sa.Column('nationality', sa.String(length=50), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('alternate_phone', sa.String(length=20), nullable=True),
        sa.Column('address_line1', sa.String(length=200), nullable=True),
        sa.Column('address_line2', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('category', sa.Enum('school_student', 'college_student', 'working_professional', 'job_seeker', 'entrepreneur', 'freelancer', 'retired', 'homemaker', 'other', name='learner_category'), nullable=False),
        sa.Column('education_level', sa.Enum('below_10th', 'class_10th', 'class_12th', 'diploma', 'undergraduate', 'postgraduate', 'doctorate', 'professional', name='education_level'), nullable=False),
        sa.Column('current_occupation', sa.String(length=200), nullable=True),
        sa.Column('organization_name', sa.String(length=200), nullable=True),
        sa.Column('work_experience_years', sa.Integer(), nullable=True),
        sa.Column('annual_income_range', sa.String(length=50), nullable=True),
        sa.Column('highest_qualification', sa.String(length=200), nullable=True),
        sa.Column('specialization', sa.String(length=200), nullable=True),
        sa.Column('university_college', sa.String(length=200), nullable=True),
        sa.Column('graduation_year', sa.Integer(), nullable=True),
        sa.Column('percentage_cgpa', sa.String(length=20), nullable=True),
        sa.Column('preferred_subjects', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_goals', sa.Text(), nullable=True),
        sa.Column('preferred_exam_types', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('study_time_availability', sa.String(length=50), nullable=True),
        sa.Column('preferred_language', sa.String(length=50), nullable=True),
        sa.Column('id_proof_type', sa.String(length=50), nullable=True),
        sa.Column('id_proof_number', sa.String(length=100), nullable=True),
        sa.Column('id_proof_verified', sa.Boolean(), nullable=True),
        sa.Column('address_proof_type', sa.String(length=50), nullable=True),
        sa.Column('address_proof_verified', sa.Boolean(), nullable=True),
        sa.Column('education_proof_verified', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('verification_level', sa.String(length=20), nullable=True),
        sa.Column('kyc_completed', sa.Boolean(), nullable=True),
        sa.Column('subscription_type', sa.String(length=50), nullable=True),
        sa.Column('subscription_start_date', sa.Date(), nullable=True),
        sa.Column('subscription_end_date', sa.Date(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('referral_code', sa.String(length=20), nullable=True),
        sa.Column('referred_by_code', sa.String(length=20), nullable=True),
        sa.Column('referral_bonus_earned', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('learner_id'),
        sa.UniqueConstraint('referral_code'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_independent_learners_learner_id'), 'independent_learners', ['learner_id'], unique=False)
    
    # Create certification_programs table
    op.create_table('certification_programs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_code', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('detailed_syllabus', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('level', sa.String(length=50), nullable=True),
        sa.Column('duration_hours', sa.Integer(), nullable=True),
        sa.Column('validity_months', sa.Integer(), nullable=True),
        sa.Column('min_education_level', sa.Enum('below_10th', 'class_10th', 'class_12th', 'diploma', 'undergraduate', 'postgraduate', 'doctorate', 'professional', name='education_level'), nullable=True),
        sa.Column('min_age', sa.Integer(), nullable=True),
        sa.Column('max_age', sa.Integer(), nullable=True),
        sa.Column('prerequisites', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('target_audience', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('base_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('discounted_price', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('pricing_tiers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bulk_discount_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('referral_discount_percent', sa.Integer(), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=True),
        sa.Column('exam_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('passing_percentage', sa.Integer(), nullable=True),
        sa.Column('max_attempts', sa.Integer(), nullable=True),
        sa.Column('retake_fee', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('study_materials', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('practice_tests_count', sa.Integer(), nullable=True),
        sa.Column('video_lectures_hours', sa.Integer(), nullable=True),
        sa.Column('downloadable_resources', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=True),
        sa.Column('enrollment_start_date', sa.Date(), nullable=True),
        sa.Column('enrollment_end_date', sa.Date(), nullable=True),
        sa.Column('total_enrollments', sa.Integer(), nullable=True),
        sa.Column('total_certifications', sa.Integer(), nullable=True),
        sa.Column('average_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('success_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('program_code')
    )
    
    # Create global_pricing_config table
    op.create_table('global_pricing_config',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('config_name', sa.String(length=100), nullable=False),
        sa.Column('config_version', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_exam_fee', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('base_certification_fee', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('base_retake_fee', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('primary_currency', sa.String(length=10), nullable=True),
        sa.Column('supported_currencies', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('currency_conversion_rates', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('student_multiplier', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('professional_multiplier', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('enterprise_multiplier', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('premium_multiplier', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('country_pricing_multipliers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('state_pricing_multipliers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('city_tier_multipliers', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bulk_discount_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('referral_discount_percent', sa.Integer(), nullable=True),
        sa.Column('loyalty_discount_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('seasonal_discounts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('promotional_campaigns', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('gateway_charges_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('convenience_fee_percent', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('tax_config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('tax_inclusive_pricing', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('effective_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('effective_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approval_status', sa.String(length=20), nullable=True),
        sa.Column('approval_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create discount_coupons table
    op.create_table('discount_coupons',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('coupon_code', sa.String(length=50), nullable=False),
        sa.Column('coupon_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('discount_type', sa.Enum('percentage', 'fixed_amount', 'bogo', 'bulk_discount', name='discount_type'), nullable=False),
        sa.Column('discount_value', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('max_discount_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('min_order_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('total_usage_limit', sa.Integer(), nullable=True),
        sa.Column('per_user_usage_limit', sa.Integer(), nullable=True),
        sa.Column('current_usage_count', sa.Integer(), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=False),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('applicable_programs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('applicable_categories', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('applicable_countries', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('first_time_users_only', sa.Boolean(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_auto_apply', sa.Boolean(), nullable=True),
        sa.Column('campaign_name', sa.String(length=100), nullable=True),
        sa.Column('campaign_source', sa.String(length=100), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.Column('approved_by', sa.String(length=100), nullable=True),
        sa.Column('approval_status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('coupon_code')
    )
    op.create_index(op.f('ix_discount_coupons_coupon_code'), 'discount_coupons', ['coupon_code'], unique=False)
    
    # Add foreign key constraint to users table for independent learner relationship
    op.add_column('users', sa.Column('independent_learner_profile', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_users_independent_learner', 'users', 'independent_learners', ['independent_learner_profile'], ['id'])


def downgrade() -> None:
    # Remove foreign key and column from users table
    op.drop_constraint('fk_users_independent_learner', 'users', type_='foreignkey')
    op.drop_column('users', 'independent_learner_profile')
    
    # Drop tables in reverse order
    op.drop_index(op.f('ix_discount_coupons_coupon_code'), table_name='discount_coupons')
    op.drop_table('discount_coupons')
    op.drop_table('global_pricing_config')
    op.drop_table('certification_programs')
    op.drop_index(op.f('ix_independent_learners_learner_id'), table_name='independent_learners')
    op.drop_table('independent_learners')
