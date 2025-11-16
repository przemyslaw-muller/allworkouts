"""Initial schema with all tables and indexes

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types using raw SQL with DO blocks for proper IF NOT EXISTS handling
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE muscle_group_enum AS ENUM (
                'chest', 'back', 'shoulders', 'biceps', 'triceps', 'forearms',
                'legs', 'glutes', 'core', 'traps', 'lats'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE unit_system_enum AS ENUM ('metric', 'imperial');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE confidence_level_enum AS ENUM ('high', 'medium', 'low');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE session_status_enum AS ENUM ('in_progress', 'completed', 'abandoned');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE record_type_enum AS ENUM ('1rm', 'set_volume', 'total_volume');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create user table
    op.create_table(
        'user',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('unit_system', sa.String(), nullable=False, server_default='metric'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_user_email', 'user', ['email'])

    # Create equipment table
    op.create_table(
        'equipment',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_equipment_name', 'equipment', ['name'])

    # Create exercise table
    op.create_table(
        'exercise',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('primary_muscle_groups', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('secondary_muscle_groups', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('default_weight', sa.Numeric(10, 2), nullable=True),
        sa.Column('default_reps', sa.Integer(), nullable=True),
        sa.Column('default_rest_time_seconds', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_exercise_name', 'exercise', ['name'])
    op.create_index('idx_exercise_primary_muscle_groups', 'exercise', ['primary_muscle_groups'], postgresql_using='gin')
    op.create_index('idx_exercise_secondary_muscle_groups', 'exercise', ['secondary_muscle_groups'], postgresql_using='gin')

    # Create exercise_equipment table
    op.create_table(
        'exercise_equipment',
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id']),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.PrimaryKeyConstraint('exercise_id', 'equipment_id'),
    )
    op.create_index('idx_exercise_equipment_equipment_id', 'exercise_equipment', ['equipment_id'])

    # Create user_equipment table
    op.create_table(
        'user_equipment',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('equipment_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id']),
        sa.PrimaryKeyConstraint('user_id', 'equipment_id'),
    )
    op.create_index('idx_user_equipment_user_id', 'user_equipment', ['user_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_user_equipment_equipment_id', 'user_equipment', ['equipment_id'])

    # Create workout_plan table
    op.create_table(
        'workout_plan',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
    )
    op.create_index('idx_workout_plan_user_id', 'workout_plan', ['user_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_workout_plan_created_at', 'workout_plan', ['user_id', 'created_at'])
    op.create_index('idx_workout_plan_name', 'workout_plan', ['user_id', 'name'], postgresql_where=sa.text('deleted_at IS NULL'))

    # Create workout_exercise table
    op.create_table(
        'workout_exercise',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workout_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('sets', sa.Integer(), nullable=False),
        sa.Column('reps_min', sa.Integer(), nullable=False),
        sa.Column('reps_max', sa.Integer(), nullable=False),
        sa.Column('rest_time_seconds', sa.Integer(), nullable=True),
        sa.Column('confidence_level', sa.String(), nullable=False, server_default='medium'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['workout_plan_id'], ['workout_plan.id']),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id']),
        sa.UniqueConstraint('workout_plan_id', 'sequence'),
    )
    op.create_index('idx_workout_exercise_workout_plan_id', 'workout_exercise', ['workout_plan_id'])
    op.create_index('idx_workout_exercise_exercise_id', 'workout_exercise', ['exercise_id'])
    op.create_index('idx_workout_exercise_sequence', 'workout_exercise', ['workout_plan_id', 'sequence'])

    # Create workout_session table
    op.create_table(
        'workout_session',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workout_plan_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='in_progress'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['workout_plan_id'], ['workout_plan.id']),
    )
    op.create_index('idx_workout_session_user_id', 'workout_session', ['user_id'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_workout_session_user_status_created', 'workout_session', ['user_id', 'status', 'created_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_workout_session_user_created', 'workout_session', ['user_id', 'created_at'], postgresql_where=sa.text('deleted_at IS NULL'))
    op.create_index('idx_workout_session_workout_plan_id', 'workout_session', ['workout_plan_id'])

    # Create exercise_session table
    op.create_table(
        'exercise_session',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('workout_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('weight', sa.Numeric(10, 2), nullable=False),
        sa.Column('reps', sa.Integer(), nullable=False),
        sa.Column('rest_time_seconds', sa.Integer(), nullable=True),
        sa.Column('set_number', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['workout_session_id'], ['workout_session.id']),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id']),
    )
    op.create_index('idx_exercise_session_workout_session_id', 'exercise_session', ['workout_session_id'])
    op.create_index('idx_exercise_session_exercise_id', 'exercise_session', ['exercise_id'])
    op.create_index('idx_exercise_session_user_exercise', 'exercise_session', ['workout_session_id', 'exercise_id'])

    # Create personal_record table
    op.create_table(
        'personal_record',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('exercise_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('record_type', sa.String(), nullable=False),
        sa.Column('value', sa.Numeric(10, 2), nullable=False),
        sa.Column('unit', sa.String(10), nullable=True),
        sa.Column('exercise_session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achieved_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['exercise_id'], ['exercise.id']),
        sa.ForeignKeyConstraint(['exercise_session_id'], ['exercise_session.id']),
        sa.UniqueConstraint('user_id', 'exercise_id', 'record_type'),
    )
    op.create_index('idx_personal_record_user_exercise', 'personal_record', ['user_id', 'exercise_id'])
    op.create_index('idx_personal_record_user_id', 'personal_record', ['user_id'])
    op.create_index('idx_personal_record_achieved_at', 'personal_record', ['user_id', 'achieved_at'])

    # Create workout_import_log table
    op.create_table(
        'workout_import_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workout_plan_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('raw_text', sa.Text(), nullable=False),
        sa.Column('parsed_exercises', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_scores', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['workout_plan_id'], ['workout_plan.id']),
    )
    op.create_index('idx_workout_import_log_user_id', 'workout_import_log', ['user_id'])
    op.create_index('idx_workout_import_log_workout_plan_id', 'workout_import_log', ['workout_plan_id'])
    op.create_index('idx_workout_import_log_created_at', 'workout_import_log', ['user_id', 'created_at'])

    # Now alter columns to use ENUM types (after tables are created)
    op.execute('ALTER TABLE "user" ALTER COLUMN unit_system DROP DEFAULT')
    op.execute('ALTER TABLE "user" ALTER COLUMN unit_system TYPE unit_system_enum USING unit_system::unit_system_enum')
    op.execute("ALTER TABLE \"user\" ALTER COLUMN unit_system SET DEFAULT 'metric'::unit_system_enum")
    
    op.execute('ALTER TABLE exercise ALTER COLUMN primary_muscle_groups TYPE muscle_group_enum[] USING primary_muscle_groups::text[]::muscle_group_enum[]')
    op.execute('ALTER TABLE exercise ALTER COLUMN secondary_muscle_groups DROP DEFAULT')
    op.execute('ALTER TABLE exercise ALTER COLUMN secondary_muscle_groups TYPE muscle_group_enum[] USING secondary_muscle_groups::text[]::muscle_group_enum[]')
    op.execute("ALTER TABLE exercise ALTER COLUMN secondary_muscle_groups SET DEFAULT '{}'")
    
    op.execute('ALTER TABLE workout_exercise ALTER COLUMN confidence_level DROP DEFAULT')
    op.execute('ALTER TABLE workout_exercise ALTER COLUMN confidence_level TYPE confidence_level_enum USING confidence_level::confidence_level_enum')
    op.execute("ALTER TABLE workout_exercise ALTER COLUMN confidence_level SET DEFAULT 'medium'::confidence_level_enum")
    
    op.execute('ALTER TABLE workout_session ALTER COLUMN status DROP DEFAULT')
    op.execute('ALTER TABLE workout_session ALTER COLUMN status TYPE session_status_enum USING status::session_status_enum')
    op.execute("ALTER TABLE workout_session ALTER COLUMN status SET DEFAULT 'in_progress'::session_status_enum")
    
    op.execute('ALTER TABLE personal_record ALTER COLUMN record_type TYPE record_type_enum USING record_type::record_type_enum')


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('workout_import_log')
    op.drop_table('personal_record')
    op.drop_table('exercise_session')
    op.drop_table('workout_session')
    op.drop_table('workout_exercise')
    op.drop_table('workout_plan')
    op.drop_table('user_equipment')
    op.drop_table('exercise_equipment')
    op.drop_table('exercise')
    op.drop_table('equipment')
    op.drop_table('user')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS record_type_enum')
    op.execute('DROP TYPE IF EXISTS session_status_enum')
    op.execute('DROP TYPE IF EXISTS confidence_level_enum')
    op.execute('DROP TYPE IF EXISTS unit_system_enum')
    op.execute('DROP TYPE IF EXISTS muscle_group_enum')
