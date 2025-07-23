"""Add certificate tables

Revision ID: 004_add_certificate_tables
Revises: 003_add_question_tables
Create Date: 2024-07-22 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_certificate_tables'
down_revision = '003_add_question_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Create certificate_templates table
    op.create_table('certificate_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('certificate_type', sa.String(length=50), nullable=False),
        sa.Column('profession_category', sa.String(length=50), nullable=False),
        sa.Column('template_data', sa.JSON(), nullable=False),
        sa.Column('background_image_url', sa.String(length=500), nullable=True),
        sa.Column('border_style', sa.JSON(), nullable=True),
        sa.Column('logo_position', sa.JSON(), nullable=True),
        sa.Column('watermark_settings', sa.JSON(), nullable=True),
        sa.Column('dimensions', sa.JSON(), nullable=True),
        sa.Column('orientation', sa.String(length=20), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certificate_templates_id'), 'certificate_templates', ['id'], unique=False)
    op.create_index(op.f('ix_certificate_templates_code'), 'certificate_templates', ['code'], unique=True)
    op.create_index(op.f('ix_certificate_templates_certificate_type'), 'certificate_templates', ['certificate_type'], unique=False)
    op.create_index(op.f('ix_certificate_templates_profession_category'), 'certificate_templates', ['profession_category'], unique=False)
    op.create_index(op.f('ix_certificate_templates_is_active'), 'certificate_templates', ['is_active'], unique=False)

    # Create certificates table
    op.create_table('certificates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('certificate_number', sa.String(length=50), nullable=False),
        sa.Column('verification_code', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=300), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('certificate_type', sa.String(length=50), nullable=False),
        sa.Column('recipient_name', sa.String(length=200), nullable=False),
        sa.Column('recipient_email', sa.String(length=255), nullable=False),
        sa.Column('student_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('issued_by', sa.String(length=200), nullable=True),
        sa.Column('subject_name', sa.String(length=200), nullable=True),
        sa.Column('course_name', sa.String(length=200), nullable=True),
        sa.Column('exam_name', sa.String(length=200), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('grade', sa.String(length=20), nullable=True),
        sa.Column('completion_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('generation_data', sa.JSON(), nullable=True),
        sa.Column('pdf_url', sa.String(length=500), nullable=True),
        sa.Column('pdf_file_size', sa.Integer(), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('blockchain_hash', sa.String(length=128), nullable=True),
        sa.Column('digital_signature', sa.Text(), nullable=True),
        sa.Column('qr_code_data', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('valid_from', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valid_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('issued_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['certificate_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certificates_id'), 'certificates', ['id'], unique=False)
    op.create_index(op.f('ix_certificates_certificate_number'), 'certificates', ['certificate_number'], unique=True)
    op.create_index(op.f('ix_certificates_verification_code'), 'certificates', ['verification_code'], unique=True)
    op.create_index(op.f('ix_certificates_certificate_type'), 'certificates', ['certificate_type'], unique=False)
    op.create_index(op.f('ix_certificates_recipient_email'), 'certificates', ['recipient_email'], unique=False)
    op.create_index(op.f('ix_certificates_status'), 'certificates', ['status'], unique=False)
    op.create_index('idx_certificate_recipient', 'certificates', ['recipient_email', 'institute_id'], unique=False)
    op.create_index('idx_certificate_status_date', 'certificates', ['status', 'issued_at'], unique=False)
    op.create_index('idx_certificate_verification', 'certificates', ['verification_code', 'status'], unique=False)

    # Create certificate_generations table
    op.create_table('certificate_generations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('batch_id', sa.String(length=100), nullable=True),
        sa.Column('generation_type', sa.String(length=50), nullable=False),
        sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('generation_params', sa.JSON(), nullable=True),
        sa.Column('certificates_requested', sa.Integer(), nullable=True),
        sa.Column('certificates_generated', sa.Integer(), nullable=True),
        sa.Column('certificates_failed', sa.Integer(), nullable=True),
        sa.Column('processing_time', sa.Float(), nullable=True),
        sa.Column('error_details', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
        sa.ForeignKeyConstraint(['requested_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['certificate_templates.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certificate_generations_batch_id'), 'certificate_generations', ['batch_id'], unique=False)


def downgrade():
    # Drop certificate_generations table
    op.drop_index(op.f('ix_certificate_generations_batch_id'), table_name='certificate_generations')
    op.drop_table('certificate_generations')
    
    # Drop certificates table
    op.drop_index('idx_certificate_verification', table_name='certificates')
    op.drop_index('idx_certificate_status_date', table_name='certificates')
    op.drop_index('idx_certificate_recipient', table_name='certificates')
    op.drop_index(op.f('ix_certificates_status'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_recipient_email'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_certificate_type'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_verification_code'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_certificate_number'), table_name='certificates')
    op.drop_index(op.f('ix_certificates_id'), table_name='certificates')
    op.drop_table('certificates')
    
    # Drop certificate_templates table
    op.drop_index(op.f('ix_certificate_templates_is_active'), table_name='certificate_templates')
    op.drop_index(op.f('ix_certificate_templates_profession_category'), table_name='certificate_templates')
    op.drop_index(op.f('ix_certificate_templates_certificate_type'), table_name='certificate_templates')
    op.drop_index(op.f('ix_certificate_templates_code'), table_name='certificate_templates')
    op.drop_index(op.f('ix_certificate_templates_id'), table_name='certificate_templates')
    op.drop_table('certificate_templates')
