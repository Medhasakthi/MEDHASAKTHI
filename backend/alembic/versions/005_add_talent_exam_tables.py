"""Add talent exam tables

Revision ID: 005_add_talent_exam_tables
Revises: 004_add_certificate_tables
Create Date: 2024-07-22 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_talent_exam_tables'
down_revision = '004_add_certificate_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create exam_centers table
    op.create_table('exam_centers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('center_code', sa.String(length=20), nullable=False),
        sa.Column('center_name', sa.String(length=300), nullable=False),
        sa.Column('address', sa.JSON(), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('pincode', sa.String(length=10), nullable=False),
        sa.Column('coordinates', sa.JSON(), nullable=True),
        sa.Column('total_capacity', sa.Integer(), nullable=False),
        sa.Column('computer_labs', sa.Integer(), nullable=True),
        sa.Column('regular_rooms', sa.Integer(), nullable=True),
        sa.Column('facilities', sa.JSON(), nullable=True),
        sa.Column('contact_person', sa.String(length=200), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('internet_speed', sa.String(length=50), nullable=True),
        sa.Column('backup_power', sa.Boolean(), nullable=True),
        sa.Column('cctv_enabled', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_exam_centers_id'), 'exam_centers', ['id'], unique=False)
    op.create_index(op.f('ix_exam_centers_center_code'), 'exam_centers', ['center_code'], unique=True)
    op.create_index(op.f('ix_exam_centers_city'), 'exam_centers', ['city'], unique=False)
    op.create_index(op.f('ix_exam_centers_state'), 'exam_centers', ['state'], unique=False)
    op.create_index(op.f('ix_exam_centers_is_active'), 'exam_centers', ['is_active'], unique=False)

    # Create talent_exams table
    op.create_table('talent_exams',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exam_code', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('exam_type', sa.String(length=50), nullable=False),
        sa.Column('class_level', sa.String(length=20), nullable=False),
        sa.Column('academic_year', sa.String(length=20), nullable=False),
        sa.Column('exam_date', sa.Date(), nullable=False),
        sa.Column('exam_time', sa.Time(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False),
        sa.Column('registration_start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('registration_end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('total_questions', sa.Integer(), nullable=False),
        sa.Column('total_marks', sa.Integer(), nullable=False),
        sa.Column('passing_marks', sa.Integer(), nullable=True),
        sa.Column('negative_marking', sa.Boolean(), nullable=True),
        sa.Column('negative_marks_per_question', sa.Float(), nullable=True),
        sa.Column('subjects', sa.JSON(), nullable=True),
        sa.Column('syllabus_details', sa.JSON(), nullable=True),
        sa.Column('registration_fee', sa.Float(), nullable=True),
        sa.Column('eligibility_criteria', sa.JSON(), nullable=True),
        sa.Column('is_proctored', sa.Boolean(), nullable=True),
        sa.Column('allow_calculator', sa.Boolean(), nullable=True),
        sa.Column('allow_rough_sheets', sa.Boolean(), nullable=True),
        sa.Column('randomize_questions', sa.Boolean(), nullable=True),
        sa.Column('result_declaration_date', sa.Date(), nullable=True),
        sa.Column('certificate_template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('max_registrations', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['certificate_template_id'], ['certificate_templates.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_talent_exams_id'), 'talent_exams', ['id'], unique=False)
    op.create_index(op.f('ix_talent_exams_exam_code'), 'talent_exams', ['exam_code'], unique=True)
    op.create_index(op.f('ix_talent_exams_exam_type'), 'talent_exams', ['exam_type'], unique=False)
    op.create_index(op.f('ix_talent_exams_class_level'), 'talent_exams', ['class_level'], unique=False)
    op.create_index(op.f('ix_talent_exams_academic_year'), 'talent_exams', ['academic_year'], unique=False)
    op.create_index(op.f('ix_talent_exams_exam_date'), 'talent_exams', ['exam_date'], unique=False)
    op.create_index(op.f('ix_talent_exams_status'), 'talent_exams', ['status'], unique=False)
    op.create_index(op.f('ix_talent_exams_is_active'), 'talent_exams', ['is_active'], unique=False)
    op.create_index('idx_talent_exam_class_year', 'talent_exams', ['class_level', 'academic_year'], unique=False)
    op.create_index('idx_talent_exam_date_status', 'talent_exams', ['exam_date', 'status'], unique=False)
    op.create_index('idx_talent_exam_registration_period', 'talent_exams', ['registration_start_date', 'registration_end_date'], unique=False)

    # Create talent_exam_registrations table
    op.create_table('talent_exam_registrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registration_number', sa.String(length=50), nullable=False),
        sa.Column('exam_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registration_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('student_name', sa.String(length=200), nullable=False),
        sa.Column('student_email', sa.String(length=255), nullable=True),
        sa.Column('student_phone', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('current_class', sa.String(length=20), nullable=True),
        sa.Column('school_name', sa.String(length=300), nullable=True),
        sa.Column('parent_name', sa.String(length=200), nullable=True),
        sa.Column('parent_email', sa.String(length=255), nullable=True),
        sa.Column('parent_phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.JSON(), nullable=True),
        sa.Column('registration_fee_paid', sa.Float(), nullable=True),
        sa.Column('payment_status', sa.String(length=30), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('exam_center_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('seat_number', sa.String(length=20), nullable=True),
        sa.Column('special_requirements', sa.JSON(), nullable=True),
        sa.Column('documents_verified', sa.Boolean(), nullable=True),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['exam_center_id'], ['exam_centers.id'], ),
        sa.ForeignKeyConstraint(['exam_id'], ['talent_exams.id'], ),
        sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_talent_exam_registrations_id'), 'talent_exam_registrations', ['id'], unique=False)
    op.create_index(op.f('ix_talent_exam_registrations_registration_number'), 'talent_exam_registrations', ['registration_number'], unique=True)
    op.create_index(op.f('ix_talent_exam_registrations_status'), 'talent_exam_registrations', ['status'], unique=False)
    op.create_index('idx_registration_exam_student', 'talent_exam_registrations', ['exam_id', 'student_id'], unique=False)
    op.create_index('idx_registration_status_date', 'talent_exam_registrations', ['status', 'registration_date'], unique=False)
    op.create_index('idx_registration_institute', 'talent_exam_registrations', ['institute_id', 'exam_id'], unique=False)

    # Create talent_exam_sessions table
    op.create_table('talent_exam_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_token', sa.String(length=100), nullable=False),
        sa.Column('exam_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('registration_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('current_question', sa.Integer(), nullable=True),
        sa.Column('questions_attempted', sa.Integer(), nullable=True),
        sa.Column('questions_answered', sa.Integer(), nullable=True),
        sa.Column('responses', sa.JSON(), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('is_submitted', sa.Boolean(), nullable=True),
        sa.Column('submission_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('proctoring_data', sa.JSON(), nullable=True),
        sa.Column('violations_count', sa.Integer(), nullable=True),
        sa.Column('browser_info', sa.JSON(), nullable=True),
        sa.Column('device_info', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['exam_id'], ['talent_exams.id'], ),
        sa.ForeignKeyConstraint(['registration_id'], ['talent_exam_registrations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_talent_exam_sessions_session_token'), 'talent_exam_sessions', ['session_token'], unique=True)
    op.create_index('idx_session_exam_registration', 'talent_exam_sessions', ['exam_id', 'registration_id'], unique=False)
    op.create_index('idx_session_status_score', 'talent_exam_sessions', ['status', 'score'], unique=False)
    op.create_index('idx_session_timing', 'talent_exam_sessions', ['started_at', 'ended_at'], unique=False)

    # Create talent_exam_notifications table
    op.create_table('talent_exam_notifications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('notification_type', sa.String(length=50), nullable=False),
        sa.Column('exam_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_class_levels', sa.JSON(), nullable=True),
        sa.Column('target_institutes', sa.JSON(), nullable=True),
        sa.Column('target_states', sa.JSON(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('send_email', sa.Boolean(), nullable=True),
        sa.Column('send_sms', sa.Boolean(), nullable=True),
        sa.Column('send_push', sa.Boolean(), nullable=True),
        sa.Column('send_in_app', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=30), nullable=True),
        sa.Column('recipients_count', sa.Integer(), nullable=True),
        sa.Column('delivered_count', sa.Integer(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['exam_id'], ['talent_exams.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_talent_exam_notifications_notification_type'), 'talent_exam_notifications', ['notification_type'], unique=False)


def downgrade():
    # Drop talent_exam_notifications table
    op.drop_index(op.f('ix_talent_exam_notifications_notification_type'), table_name='talent_exam_notifications')
    op.drop_table('talent_exam_notifications')
    
    # Drop talent_exam_sessions table
    op.drop_index('idx_session_timing', table_name='talent_exam_sessions')
    op.drop_index('idx_session_status_score', table_name='talent_exam_sessions')
    op.drop_index('idx_session_exam_registration', table_name='talent_exam_sessions')
    op.drop_index(op.f('ix_talent_exam_sessions_session_token'), table_name='talent_exam_sessions')
    op.drop_table('talent_exam_sessions')
    
    # Drop talent_exam_registrations table
    op.drop_index('idx_registration_institute', table_name='talent_exam_registrations')
    op.drop_index('idx_registration_status_date', table_name='talent_exam_registrations')
    op.drop_index('idx_registration_exam_student', table_name='talent_exam_registrations')
    op.drop_index(op.f('ix_talent_exam_registrations_status'), table_name='talent_exam_registrations')
    op.drop_index(op.f('ix_talent_exam_registrations_registration_number'), table_name='talent_exam_registrations')
    op.drop_index(op.f('ix_talent_exam_registrations_id'), table_name='talent_exam_registrations')
    op.drop_table('talent_exam_registrations')
    
    # Drop talent_exams table
    op.drop_index('idx_talent_exam_registration_period', table_name='talent_exams')
    op.drop_index('idx_talent_exam_date_status', table_name='talent_exams')
    op.drop_index('idx_talent_exam_class_year', table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_is_active'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_status'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_exam_date'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_academic_year'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_class_level'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_exam_type'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_exam_code'), table_name='talent_exams')
    op.drop_index(op.f('ix_talent_exams_id'), table_name='talent_exams')
    op.drop_table('talent_exams')
    
    # Drop exam_centers table
    op.drop_index(op.f('ix_exam_centers_is_active'), table_name='exam_centers')
    op.drop_index(op.f('ix_exam_centers_state'), table_name='exam_centers')
    op.drop_index(op.f('ix_exam_centers_city'), table_name='exam_centers')
    op.drop_index(op.f('ix_exam_centers_center_code'), table_name='exam_centers')
    op.drop_index(op.f('ix_exam_centers_id'), table_name='exam_centers')
    op.drop_table('exam_centers')
