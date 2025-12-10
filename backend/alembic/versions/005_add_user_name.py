"""Add name field to user table

Revision ID: 005_add_user_name
Revises: 004_add_workout_hierarchy
Create Date: 2025-01-10
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "005_add_user_name"
down_revision = "004_add_workout_hierarchy"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add name column to user table
    op.add_column("user", sa.Column("name", sa.String(100), nullable=True))


def downgrade() -> None:
    # Remove name column from user table
    op.drop_column("user", "name")
