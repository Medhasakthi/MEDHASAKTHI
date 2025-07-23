"""Add school education support

Revision ID: 006_add_school_education_support
Revises: 005_add_talent_exam_tables
Create Date: 2024-07-22 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_school_education_support'
down_revision = '005_add_talent_exam_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to institutes table for school support
    op.add_column('institutes', sa.Column('institute_type', sa.String(length=50), nullable=True))
    op.add_column('institutes', sa.Column('education_level', sa.String(length=50), nullable=True))
    op.add_column('institutes', sa.Column('education_board', sa.String(length=50), nullable=True))
    op.add_column('institutes', sa.Column('medium_of_instruction', sa.JSON(), nullable=True))
    op.add_column('institutes', sa.Column('classes_offered', sa.JSON(), nullable=True))
    op.add_column('institutes', sa.Column('streams_offered', sa.JSON(), nullable=True))
    op.add_column('institutes', sa.Column('school_registration_number', sa.String(length=100), nullable=True))
    op.add_column('institutes', sa.Column('affiliation_number', sa.String(length=100), nullable=True))
    op.add_column('institutes', sa.Column('recognition_status', sa.String(length=50), nullable=True))
    op.add_column('institutes', sa.Column('establishment_year', sa.Integer(), nullable=True))
    op.add_column('institutes', sa.Column('total_students', sa.Integer(), nullable=True))
    op.add_column('institutes', sa.Column('total_teachers', sa.Integer(), nullable=True))
    op.add_column('institutes', sa.Column('total_classrooms', sa.Integer(), nullable=True))
    op.add_column('institutes', sa.Column('has_library', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('has_laboratory', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('has_computer_lab', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('has_playground', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('facilities', sa.JSON(), nullable=True))
    op.add_column('institutes', sa.Column('transport_facility', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('hostel_facility', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('canteen_facility', sa.Boolean(), nullable=True))
    op.add_column('institutes', sa.Column('academic_calendar', sa.JSON(), nullable=True))
    op.add_column('institutes', sa.Column('examination_pattern', sa.JSON(), nullable=True))
    op.add_column('institutes', sa.Column('grading_system', sa.String(length=50), nullable=True))
    op.add_column('institutes', sa.Column('principal_name', sa.String(length=200), nullable=True))
    op.add_column('institutes', sa.Column('principal_email', sa.String(length=255), nullable=True))
    op.add_column('institutes', sa.Column('principal_phone', sa.String(length=20), nullable=True))
    op.add_column('institutes', sa.Column('contact_person_name', sa.String(length=200), nullable=True))
    op.add_column('institutes', sa.Column('contact_person_designation', sa.String(length=100), nullable=True))

    # Create indexes for new institute columns
    op.create_index(op.f('ix_institutes_institute_type'), 'institutes', ['institute_type'], unique=False)
    op.create_index(op.f('ix_institutes_education_board'), 'institutes', ['education_board'], unique=False)

    # Add new columns to students table for school support
    op.add_column('students', sa.Column('class_level', sa.String(length=20), nullable=True))
    op.add_column('students', sa.Column('section', sa.String(length=10), nullable=True))
    op.add_column('students', sa.Column('education_board', sa.String(length=50), nullable=True))
    op.add_column('students', sa.Column('medium_of_instruction', sa.String(length=50), nullable=True))
    op.add_column('students', sa.Column('stream', sa.String(length=30), nullable=True))
    op.add_column('students', sa.Column('previous_class', sa.String(length=20), nullable=True))
    op.add_column('students', sa.Column('promotion_status', sa.String(length=30), nullable=True))
    op.add_column('students', sa.Column('subjects_enrolled', sa.JSON(), nullable=True))
    op.add_column('students', sa.Column('current_grade', sa.String(length=10), nullable=True))
    op.add_column('students', sa.Column('current_percentage', sa.Float(), nullable=True))
    op.add_column('students', sa.Column('attendance_percentage', sa.Float(), nullable=True))
    op.add_column('students', sa.Column('house', sa.String(length=50), nullable=True))
    op.add_column('students', sa.Column('transport_required', sa.Boolean(), nullable=True))
    op.add_column('students', sa.Column('hostel_required', sa.Boolean(), nullable=True))
    op.add_column('students', sa.Column('special_needs', sa.JSON(), nullable=True))

    # Create indexes for new student columns
    op.create_index(op.f('ix_students_class_level'), 'students', ['class_level'], unique=False)
    op.create_index(op.f('ix_students_academic_year'), 'students', ['academic_year'], unique=False)

    # Update academic_year column length in students table
    op.alter_column('students', 'academic_year',
                    existing_type=sa.VARCHAR(length=10),
                    type_=sa.String(length=20),
                    existing_nullable=True)

    # Create school_subjects table
    op.create_table('school_subjects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('display_name', sa.String(length=150), nullable=True),
        sa.Column('education_board', sa.String(length=50), nullable=False),
        sa.Column('class_level', sa.String(length=20), nullable=False),
        sa.Column('education_level', sa.String(length=30), nullable=False),
        sa.Column('is_core_subject', sa.Boolean(), nullable=True),
        sa.Column('is_optional', sa.Boolean(), nullable=True),
        sa.Column('is_language', sa.Boolean(), nullable=True),
        sa.Column('subject_category', sa.String(length=50), nullable=True),
        sa.Column('applicable_streams', sa.JSON(), nullable=True),
        sa.Column('syllabus_outline', sa.JSON(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('assessment_pattern', sa.JSON(), nullable=True),
        sa.Column('prerequisite_subjects', sa.JSON(), nullable=True),
        sa.Column('next_level_subjects', sa.JSON(), nullable=True),
        sa.Column('has_practical', sa.Boolean(), nullable=True),
        sa.Column('theory_marks', sa.Integer(), nullable=True),
        sa.Column('practical_marks', sa.Integer(), nullable=True),
        sa.Column('internal_assessment_marks', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_school_subjects_id'), 'school_subjects', ['id'], unique=False)
    op.create_index(op.f('ix_school_subjects_education_board'), 'school_subjects', ['education_board'], unique=False)
    op.create_index(op.f('ix_school_subjects_class_level'), 'school_subjects', ['class_level'], unique=False)
    op.create_index(op.f('ix_school_subjects_education_level'), 'school_subjects', ['education_level'], unique=False)
    op.create_index(op.f('ix_school_subjects_is_active'), 'school_subjects', ['is_active'], unique=False)
    op.create_index('idx_school_subject_board_class', 'school_subjects', ['education_board', 'class_level'], unique=False)
    op.create_index('idx_school_subject_level_category', 'school_subjects', ['education_level', 'subject_category'], unique=False)
    op.create_index('idx_school_subject_core_optional', 'school_subjects', ['is_core_subject', 'is_optional'], unique=False)

    # Create school_topics table
    op.create_table('school_topics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=250), nullable=True),
        sa.Column('subject_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('parent_topic_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('level', sa.Integer(), nullable=True),
        sa.Column('sequence_order', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('key_concepts', sa.JSON(), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=True),
        sa.Column('estimated_hours', sa.Float(), nullable=True),
        sa.Column('weightage_percentage', sa.Float(), nullable=True),
        sa.Column('prerequisite_topics', sa.JSON(), nullable=True),
        sa.Column('assessment_methods', sa.JSON(), nullable=True),
        sa.Column('sample_questions', sa.JSON(), nullable=True),
        sa.Column('reference_materials', sa.JSON(), nullable=True),
        sa.Column('practical_activities', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_topic_id'], ['school_topics.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['school_subjects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_school_topics_id'), 'school_topics', ['id'], unique=False)
    op.create_index(op.f('ix_school_topics_is_active'), 'school_topics', ['is_active'], unique=False)
    op.create_index('idx_school_topic_subject_level', 'school_topics', ['subject_id', 'level'], unique=False)
    op.create_index('idx_school_topic_sequence', 'school_topics', ['subject_id', 'sequence_order'], unique=False)
    op.create_index('idx_school_topic_difficulty', 'school_topics', ['difficulty_level', 'weightage_percentage'], unique=False)

    # Create school_curricula table
    op.create_table('school_curricula',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('education_board', sa.String(length=50), nullable=False),
        sa.Column('class_level', sa.String(length=20), nullable=False),
        sa.Column('academic_year', sa.String(length=20), nullable=False),
        sa.Column('stream', sa.String(length=30), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('objectives', sa.JSON(), nullable=True),
        sa.Column('learning_outcomes', sa.JSON(), nullable=True),
        sa.Column('core_subjects', sa.JSON(), nullable=True),
        sa.Column('optional_subjects', sa.JSON(), nullable=True),
        sa.Column('co_curricular_subjects', sa.JSON(), nullable=True),
        sa.Column('assessment_pattern', sa.JSON(), nullable=True),
        sa.Column('grading_system', sa.JSON(), nullable=True),
        sa.Column('promotion_criteria', sa.JSON(), nullable=True),
        sa.Column('total_teaching_hours', sa.Integer(), nullable=True),
        sa.Column('subject_wise_hours', sa.JSON(), nullable=True),
        sa.Column('internal_assessment_weightage', sa.Float(), nullable=True),
        sa.Column('external_assessment_weightage', sa.Float(), nullable=True),
        sa.Column('practical_assessment_weightage', sa.Float(), nullable=True),
        sa.Column('has_board_exam', sa.Boolean(), nullable=True),
        sa.Column('board_exam_pattern', sa.JSON(), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_school_curricula_education_board'), 'school_curricula', ['education_board'], unique=False)
    op.create_index(op.f('ix_school_curricula_class_level'), 'school_curricula', ['class_level'], unique=False)
    op.create_index(op.f('ix_school_curricula_academic_year'), 'school_curricula', ['academic_year'], unique=False)
    op.create_index(op.f('ix_school_curricula_is_active'), 'school_curricula', ['is_active'], unique=False)
    op.create_index('idx_curriculum_board_class_year', 'school_curricula', ['education_board', 'class_level', 'academic_year'], unique=False)
    op.create_index('idx_curriculum_stream_current', 'school_curricula', ['stream', 'is_current'], unique=False)
    op.create_index('idx_curriculum_board_exam', 'school_curricula', ['has_board_exam', 'education_board'], unique=False)

    # Create school_academic_years table
    op.create_table('school_academic_years',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('year_code', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('term_structure', sa.JSON(), nullable=True),
        sa.Column('admission_start_date', sa.Date(), nullable=True),
        sa.Column('admission_end_date', sa.Date(), nullable=True),
        sa.Column('exam_schedule', sa.JSON(), nullable=True),
        sa.Column('holiday_calendar', sa.JSON(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('year_code')
    )
    op.create_index(op.f('ix_school_academic_years_year_code'), 'school_academic_years', ['year_code'], unique=False)
    op.create_index(op.f('ix_school_academic_years_is_current'), 'school_academic_years', ['is_current'], unique=False)
    op.create_index(op.f('ix_school_academic_years_is_active'), 'school_academic_years', ['is_active'], unique=False)

    # Create school_grading_systems table
    op.create_table('school_grading_systems',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('education_board', sa.String(length=50), nullable=False),
        sa.Column('applicable_classes', sa.JSON(), nullable=True),
        sa.Column('grading_scale', sa.JSON(), nullable=True),
        sa.Column('grade_points', sa.JSON(), nullable=True),
        sa.Column('calculation_method', sa.String(length=50), nullable=True),
        sa.Column('passing_criteria', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_school_grading_systems_education_board'), 'school_grading_systems', ['education_board'], unique=False)
    op.create_index(op.f('ix_school_grading_systems_is_active'), 'school_grading_systems', ['is_active'], unique=False)

    # Set default values for new columns
    op.execute("UPDATE institutes SET institute_type = 'college' WHERE institute_type IS NULL")
    op.execute("UPDATE institutes SET total_students = 0 WHERE total_students IS NULL")
    op.execute("UPDATE institutes SET total_teachers = 0 WHERE total_teachers IS NULL")
    op.execute("UPDATE institutes SET total_classrooms = 0 WHERE total_classrooms IS NULL")
    op.execute("UPDATE institutes SET has_library = false WHERE has_library IS NULL")
    op.execute("UPDATE institutes SET has_laboratory = false WHERE has_laboratory IS NULL")
    op.execute("UPDATE institutes SET has_computer_lab = false WHERE has_computer_lab IS NULL")
    op.execute("UPDATE institutes SET has_playground = false WHERE has_playground IS NULL")
    op.execute("UPDATE institutes SET transport_facility = false WHERE transport_facility IS NULL")
    op.execute("UPDATE institutes SET hostel_facility = false WHERE hostel_facility IS NULL")
    op.execute("UPDATE institutes SET canteen_facility = false WHERE canteen_facility IS NULL")
    
    op.execute("UPDATE students SET attendance_percentage = 0.0 WHERE attendance_percentage IS NULL")
    op.execute("UPDATE students SET transport_required = false WHERE transport_required IS NULL")
    op.execute("UPDATE students SET hostel_required = false WHERE hostel_required IS NULL")


def downgrade():
    # Drop school education tables
    op.drop_table('school_grading_systems')
    op.drop_table('school_academic_years')
    op.drop_table('school_curricula')
    op.drop_table('school_topics')
    op.drop_table('school_subjects')
    
    # Remove new columns from students table
    op.drop_index(op.f('ix_students_academic_year'), table_name='students')
    op.drop_index(op.f('ix_students_class_level'), table_name='students')
    op.drop_column('students', 'special_needs')
    op.drop_column('students', 'hostel_required')
    op.drop_column('students', 'transport_required')
    op.drop_column('students', 'house')
    op.drop_column('students', 'attendance_percentage')
    op.drop_column('students', 'current_percentage')
    op.drop_column('students', 'current_grade')
    op.drop_column('students', 'subjects_enrolled')
    op.drop_column('students', 'promotion_status')
    op.drop_column('students', 'previous_class')
    op.drop_column('students', 'stream')
    op.drop_column('students', 'medium_of_instruction')
    op.drop_column('students', 'education_board')
    op.drop_column('students', 'section')
    op.drop_column('students', 'class_level')
    
    # Revert academic_year column length
    op.alter_column('students', 'academic_year',
                    existing_type=sa.String(length=20),
                    type_=sa.VARCHAR(length=10),
                    existing_nullable=True)
    
    # Remove new columns from institutes table
    op.drop_index(op.f('ix_institutes_education_board'), table_name='institutes')
    op.drop_index(op.f('ix_institutes_institute_type'), table_name='institutes')
    op.drop_column('institutes', 'contact_person_designation')
    op.drop_column('institutes', 'contact_person_name')
    op.drop_column('institutes', 'principal_phone')
    op.drop_column('institutes', 'principal_email')
    op.drop_column('institutes', 'principal_name')
    op.drop_column('institutes', 'grading_system')
    op.drop_column('institutes', 'examination_pattern')
    op.drop_column('institutes', 'academic_calendar')
    op.drop_column('institutes', 'canteen_facility')
    op.drop_column('institutes', 'hostel_facility')
    op.drop_column('institutes', 'transport_facility')
    op.drop_column('institutes', 'facilities')
    op.drop_column('institutes', 'has_playground')
    op.drop_column('institutes', 'has_computer_lab')
    op.drop_column('institutes', 'has_laboratory')
    op.drop_column('institutes', 'has_library')
    op.drop_column('institutes', 'total_classrooms')
    op.drop_column('institutes', 'total_teachers')
    op.drop_column('institutes', 'total_students')
    op.drop_column('institutes', 'establishment_year')
    op.drop_column('institutes', 'recognition_status')
    op.drop_column('institutes', 'affiliation_number')
    op.drop_column('institutes', 'school_registration_number')
    op.drop_column('institutes', 'streams_offered')
    op.drop_column('institutes', 'classes_offered')
    op.drop_column('institutes', 'medium_of_instruction')
    op.drop_column('institutes', 'education_board')
    op.drop_column('institutes', 'education_level')
    op.drop_column('institutes', 'institute_type')
