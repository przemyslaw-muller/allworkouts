"""Make exercise_session_id nullable in personal_record

Revision ID: 003_nullable_exercise_session_id
Revises: 002_seed_data
Create Date: 2024-01-01 00:02:00

This allows manual personal record entries that are not linked to a workout session.
"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '003_nullable_exercise_session_id'
down_revision = '002_seed_data'
branch_labels = None
depends_on = None


def upgrade():
    # Make exercise_session_id nullable to allow manual PR entries
    op.alter_column(
        'personal_record',
        'exercise_session_id',
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=True,
    )


def downgrade():
    # Note: This will fail if there are any NULL values
    op.alter_column(
        'personal_record',
        'exercise_session_id',
        existing_type=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False,
    )
