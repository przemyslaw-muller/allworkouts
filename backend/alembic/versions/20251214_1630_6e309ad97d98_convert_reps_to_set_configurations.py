"""convert_reps_to_set_configurations

Revision ID: 6e309ad97d98
Revises: fabe8ba45ba0
Create Date: 2025-12-14 16:30:16.546528

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '6e309ad97d98'
down_revision = 'fabe8ba45ba0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new column
    op.add_column('workout_exercise', sa.Column('set_configurations', postgresql.JSONB, nullable=True))
    
    # Convert existing data: create array of set configs from sets, reps_min, reps_max
    op.execute("""
        UPDATE workout_exercise
        SET set_configurations = (
            SELECT json_agg(
                json_build_object(
                    'set_number', s.set_num,
                    'reps_min', reps_min,
                    'reps_max', reps_max
                )
            )
            FROM generate_series(1, sets) AS s(set_num)
        )
    """)
    
    # Make set_configurations not nullable
    op.alter_column('workout_exercise', 'set_configurations', nullable=False)
    
    # Drop old columns
    op.drop_column('workout_exercise', 'sets')
    op.drop_column('workout_exercise', 'reps_min')
    op.drop_column('workout_exercise', 'reps_max')


def downgrade() -> None:
    # Add back old columns
    op.add_column('workout_exercise', sa.Column('sets', sa.Integer(), nullable=True))
    op.add_column('workout_exercise', sa.Column('reps_min', sa.Integer(), nullable=True))
    op.add_column('workout_exercise', sa.Column('reps_max', sa.Integer(), nullable=True))
    
    # Convert data back: count sets, take first set's reps
    op.execute("""
        UPDATE workout_exercise
        SET 
            sets = jsonb_array_length(set_configurations),
            reps_min = (set_configurations->0->>'reps_min')::integer,
            reps_max = (set_configurations->0->>'reps_max')::integer
    """)
    
    # Make columns not nullable
    op.alter_column('workout_exercise', 'sets', nullable=False)
    op.alter_column('workout_exercise', 'reps_min', nullable=False)
    op.alter_column('workout_exercise', 'reps_max', nullable=False)
    
    # Drop new column
    op.drop_column('workout_exercise', 'set_configurations')
