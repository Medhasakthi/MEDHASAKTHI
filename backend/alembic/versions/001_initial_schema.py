"""Initial schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.execute("CREATE TYPE gender AS ENUM ('male', 'female', 'other', 'prefer_not_to_say')")
    op.execute("CREATE TYPE userrole AS ENUM ('super_admin', 'institute_admin', 'institute_staff', 'teacher', 'student', 'independent_learner')")
    op.execute("CREATE TYPE learner_category AS ENUM ('school_student', 'college_student', 'working_professional', 'job_seeker', 'entrepreneur', 'freelancer', 'retired', 'homemaker', 'other')")
    op.execute("CREATE TYPE education_level AS ENUM ('below_10th', 'class_10th', 'class_12th', 'diploma', 'undergraduate', 'postgraduate', 'doctorate', 'professional')")
    op.execute("CREATE TYPE upi_provider AS ENUM ('phonepe', 'googlepay', 'paytm', 'bhim', 'amazon_pay', 'whatsapp_pay', 'other')")
    op.execute("CREATE TYPE upi_payment_status AS ENUM ('pending', 'success', 'failed', 'expired', 'cancelled')")
    op.execute("CREATE TYPE discount_type AS ENUM ('percentage', 'fixed_amount', 'bogo', 'bulk_discount')")
    
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=200), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('super_admin', 'institute_admin', 'institute_staff', 'teacher', 'student', 'independent_learner', name='userrole'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_email_verified', sa.Boolean(), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    
    # Create institutes table
    op.create_table('institutes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('established_year', sa.Integer(), nullable=True),
        sa.Column('affiliation', sa.String(length=200), nullable=True),
        sa.Column('principal_name', sa.String(length=200), nullable=True),
        sa.Column('total_students', sa.Integer(), nullable=True),
        sa.Column('total_teachers', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('subscription_type', sa.String(length=50), nullable=True),
        sa.Column('subscription_start_date', sa.Date(), nullable=True),
        sa.Column('subscription_end_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_institutes_code'), 'institutes', ['code'], unique=False)
    
    # Create students table
    op.create_table('students',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('student_id', sa.String(length=50), nullable=False),
        sa.Column('roll_number', sa.String(length=50), nullable=True),
        sa.Column('admission_number', sa.String(length=50), nullable=True),
        sa.Column('class_level', sa.String(length=20), nullable=False),
        sa.Column('section', sa.String(length=10), nullable=True),
        sa.Column('academic_year', sa.String(length=20), nullable=True),
        sa.Column('education_board', sa.String(length=50), nullable=True),
        sa.Column('medium_of_instruction', sa.String(length=50), nullable=True),
        sa.Column('stream', sa.String(length=50), nullable=True),
        sa.Column('father_name', sa.String(length=200), nullable=True),
        sa.Column('mother_name', sa.String(length=200), nullable=True),
        sa.Column('guardian_phone', sa.String(length=20), nullable=True),
        sa.Column('guardian_email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=200), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('blood_group', sa.String(length=5), nullable=True),
        sa.Column('house', sa.String(length=50), nullable=True),
        sa.Column('transport_required', sa.Boolean(), nullable=True),
        sa.Column('hostel_required', sa.Boolean(), nullable=True),
        sa.Column('auto_generated_email', sa.String(length=255), nullable=True),
        sa.Column('default_password_changed', sa.Boolean(), nullable=True),
        sa.Column('first_login_completed', sa.Boolean(), nullable=True),
        sa.Column('password_reset_required', sa.Boolean(), nullable=True),
        sa.Column('average_score', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('total_exams_taken', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('institute_id', 'student_id', name='uq_institute_student_id')
    )
    op.create_index(op.f('ix_students_auto_email'), 'students', ['auto_generated_email'], unique=False)
    op.create_index(op.f('ix_students_class_level'), 'students', ['class_level'], unique=False)
    op.create_index(op.f('ix_students_institute_id'), 'students', ['institute_id'], unique=False)
    
    # Create teachers table
    op.create_table('teachers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('institute_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('teacher_id', sa.String(length=50), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('subjects', sa.Text(), nullable=True),
        sa.Column('qualifications', sa.Text(), nullable=True),
        sa.Column('subject_specialization', sa.String(length=200), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('designation', sa.String(length=100), nullable=True),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('office_phone', sa.String(length=20), nullable=True),
        sa.Column('office_location', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=15), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=100), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=15), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('blood_group', sa.String(length=5), nullable=True),
        sa.Column('aadhar_number', sa.String(length=20), nullable=True),
        sa.Column('pan_number', sa.String(length=15), nullable=True),
        sa.Column('classes_assigned', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('subjects_assigned', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_class_teacher', sa.Boolean(), nullable=True),
        sa.Column('class_teacher_of', sa.String(length=50), nullable=True),
        sa.Column('auto_generated_email', sa.String(length=255), nullable=True),
        sa.Column('default_password_changed', sa.Boolean(), nullable=True),
        sa.Column('first_login_completed', sa.Boolean(), nullable=True),
        sa.Column('password_reset_required', sa.Boolean(), nullable=True),
        sa.Column('joining_date', sa.Date(), nullable=True),
        sa.Column('salary_grade', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('institute_id', 'teacher_id', name='uq_institute_teacher_id')
    )
    op.create_index(op.f('ix_teachers_auto_email'), 'teachers', ['auto_generated_email'], unique=False)
    op.create_index(op.f('ix_teachers_department'), 'teachers', ['department'], unique=False)
    op.create_index(op.f('ix_teachers_institute_id'), 'teachers', ['institute_id'], unique=False)
    op.create_index(op.f('ix_teachers_subject'), 'teachers', ['subject_specialization'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_teachers_subject'), table_name='teachers')
    op.drop_index(op.f('ix_teachers_institute_id'), table_name='teachers')
    op.drop_index(op.f('ix_teachers_department'), table_name='teachers')
    op.drop_index(op.f('ix_teachers_auto_email'), table_name='teachers')
    op.drop_table('teachers')
    
    op.drop_index(op.f('ix_students_institute_id'), table_name='students')
    op.drop_index(op.f('ix_students_class_level'), table_name='students')
    op.drop_index(op.f('ix_students_auto_email'), table_name='students')
    op.drop_table('students')
    
    op.drop_index(op.f('ix_institutes_code'), table_name='institutes')
    op.drop_table('institutes')
    
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS discount_type")
    op.execute("DROP TYPE IF EXISTS upi_payment_status")
    op.execute("DROP TYPE IF EXISTS upi_provider")
    op.execute("DROP TYPE IF EXISTS education_level")
    op.execute("DROP TYPE IF EXISTS learner_category")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS gender")
