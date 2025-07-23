"""Add UPI payment system

Revision ID: 003_upi_payments
Revises: 002_independent_learners
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_upi_payments'
down_revision = '002_independent_learners'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create upi_configuration table
    op.create_table('upi_configuration',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('upi_id', sa.String(length=100), nullable=False),
        sa.Column('upi_name', sa.String(length=200), nullable=False),
        sa.Column('provider', sa.Enum('phonepe', 'googlepay', 'paytm', 'bhim', 'amazon_pay', 'whatsapp_pay', 'other', name='upi_provider'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('qr_code_url', sa.String(length=500), nullable=True),
        sa.Column('qr_code_data', sa.Text(), nullable=True),
        sa.Column('min_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('max_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('daily_limit', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('auto_generate_qr', sa.Boolean(), nullable=True),
        sa.Column('include_amount_in_qr', sa.Boolean(), nullable=True),
        sa.Column('include_note_in_qr', sa.Boolean(), nullable=True),
        sa.Column('require_screenshot', sa.Boolean(), nullable=True),
        sa.Column('auto_verify_payments', sa.Boolean(), nullable=True),
        sa.Column('verification_timeout_minutes', sa.Integer(), nullable=True),
        sa.Column('notify_on_payment', sa.Boolean(), nullable=True),
        sa.Column('notification_email', sa.String(length=255), nullable=True),
        sa.Column('notification_phone', sa.String(length=20), nullable=True),
        sa.Column('total_transactions', sa.Integer(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('success_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create upi_payment_requests table
    op.create_table('upi_payment_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_id', sa.String(length=100), nullable=False),
        sa.Column('upi_config_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('user_phone', sa.String(length=20), nullable=True),
        sa.Column('user_name', sa.String(length=200), nullable=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('reference_id', sa.String(length=100), nullable=True),
        sa.Column('upi_id', sa.String(length=100), nullable=False),
        sa.Column('upi_name', sa.String(length=200), nullable=False),
        sa.Column('payment_note', sa.String(length=200), nullable=True),
        sa.Column('qr_code_url', sa.String(length=500), nullable=True),
        sa.Column('qr_code_data', sa.Text(), nullable=True),
        sa.Column('upi_deep_link', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'success', 'failed', 'expired', 'cancelled', name='upi_payment_status'), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('screenshot_url', sa.String(length=500), nullable=True),
        sa.Column('verification_status', sa.String(length=20), nullable=True),
        sa.Column('verified_by', sa.String(length=100), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=True),
        sa.Column('max_retries', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['upi_config_id'], ['upi_configuration.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_id')
    )
    op.create_index(op.f('ix_upi_payment_requests_payment_id'), 'upi_payment_requests', ['payment_id'], unique=False)
    
    # Create upi_payment_verifications table
    op.create_table('upi_payment_verifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('verified_by', sa.String(length=100), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('verification_notes', sa.Text(), nullable=True),
        sa.Column('verified_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('verified_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('verified_timestamp', sa.DateTime(timezone=True), nullable=True),
        sa.Column('admin_ip', sa.String(length=50), nullable=True),
        sa.Column('admin_user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['payment_request_id'], ['upi_payment_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create upi_payment_notifications table
    op.create_table('upi_payment_notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_request_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('recipient_type', sa.String(length=20), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=True),
        sa.Column('recipient_phone', sa.String(length=20), nullable=True),
        sa.Column('subject', sa.String(length=200), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('template_used', sa.String(length=100), nullable=True),
        sa.Column('delivery_status', sa.String(length=20), nullable=True),
        sa.Column('delivery_attempts', sa.Integer(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['payment_request_id'], ['upi_payment_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create upi_payment_analytics table
    op.create_table('upi_payment_analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('upi_config_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('total_requests', sa.Integer(), nullable=True),
        sa.Column('successful_payments', sa.Integer(), nullable=True),
        sa.Column('failed_payments', sa.Integer(), nullable=True),
        sa.Column('pending_payments', sa.Integer(), nullable=True),
        sa.Column('total_amount_requested', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_amount_received', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('average_transaction_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('success_rate', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('average_verification_time', sa.Integer(), nullable=True),
        sa.Column('unique_users', sa.Integer(), nullable=True),
        sa.Column('repeat_users', sa.Integer(), nullable=True),
        sa.Column('provider_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('amount_range_breakdown', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['upi_config_id'], ['upi_configuration.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create additional tables for exam registrations and certificates
    op.create_table('independent_exam_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('learner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registration_number', sa.String(length=50), nullable=False),
        sa.Column('registration_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('exam_date', sa.Date(), nullable=True),
        sa.Column('exam_time', sa.String(length=20), nullable=True),
        sa.Column('exam_center', sa.String(length=200), nullable=True),
        sa.Column('amount_paid', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('payment_status', sa.String(length=20), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('attempt_number', sa.Integer(), nullable=True),
        sa.Column('exam_started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('exam_completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('score_obtained', sa.Integer(), nullable=True),
        sa.Column('total_score', sa.Integer(), nullable=True),
        sa.Column('percentage', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('result', sa.String(length=20), nullable=True),
        sa.Column('grade', sa.String(length=10), nullable=True),
        sa.Column('proctoring_enabled', sa.Boolean(), nullable=True),
        sa.Column('proctoring_violations', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('proctoring_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['independent_learners.id'], ),
        sa.ForeignKeyConstraint(['program_id'], ['certification_programs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('registration_number')
    )
    
    # Create independent_certificates table
    op.create_table('independent_certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('learner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('program_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('certificate_number', sa.String(length=50), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('learner_name', sa.String(length=200), nullable=False),
        sa.Column('program_title', sa.String(length=200), nullable=False),
        sa.Column('score_achieved', sa.Integer(), nullable=True),
        sa.Column('grade_obtained', sa.String(length=10), nullable=True),
        sa.Column('verification_code', sa.String(length=100), nullable=False),
        sa.Column('blockchain_hash', sa.String(length=256), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('certificate_url', sa.String(length=500), nullable=True),
        sa.Column('certificate_template', sa.String(length=100), nullable=True),
        sa.Column('digital_signature', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('revocation_reason', sa.String(length=200), nullable=True),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['independent_learners.id'], ),
        sa.ForeignKeyConstraint(['program_id'], ['certification_programs.id'], ),
        sa.ForeignKeyConstraint(['registration_id'], ['independent_exam_registrations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('certificate_number'),
        sa.UniqueConstraint('verification_code')
    )
    
    # Create independent_payments table
    op.create_table('independent_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('learner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_id', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('payment_type', sa.String(length=50), nullable=True),
        sa.Column('gateway', sa.String(length=50), nullable=True),
        sa.Column('gateway_transaction_id', sa.String(length=200), nullable=True),
        sa.Column('gateway_payment_id', sa.String(length=200), nullable=True),
        sa.Column('gateway_order_id', sa.String(length=200), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('billing_name', sa.String(length=200), nullable=True),
        sa.Column('billing_email', sa.String(length=200), nullable=True),
        sa.Column('billing_phone', sa.String(length=20), nullable=True),
        sa.Column('billing_address', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('initiated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failure_reason', sa.String(length=500), nullable=True),
        sa.Column('refund_amount', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('refund_status', sa.String(length=20), nullable=True),
        sa.Column('refund_reason', sa.String(length=500), nullable=True),
        sa.Column('refunded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['learner_id'], ['independent_learners.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('independent_payments')
    op.drop_table('independent_certificates')
    op.drop_table('independent_exam_registrations')
    op.drop_table('upi_payment_analytics')
    op.drop_table('upi_payment_notifications')
    op.drop_table('upi_payment_verifications')
    op.drop_index(op.f('ix_upi_payment_requests_payment_id'), table_name='upi_payment_requests')
    op.drop_table('upi_payment_requests')
    op.drop_table('upi_configuration')
