"""add_status_to_import_log

Revision ID: fabe8ba45ba0
Revises: cbdbb91967a7
Create Date: 2025-12-14 13:24:49.022235

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = 'fabe8ba45ba0'
down_revision = 'cbdbb91967a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add status, result, and error columns to workout_import_log
    op.add_column('workout_import_log', sa.Column('status', sa.String(50), nullable=False, server_default='pending'))
    op.add_column('workout_import_log', sa.Column('result', postgresql.JSONB, nullable=True))
    op.add_column('workout_import_log', sa.Column('error', sa.Text, nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('workout_import_log', 'error')
    op.drop_column('workout_import_log', 'result')
    op.drop_column('workout_import_log', 'status')
