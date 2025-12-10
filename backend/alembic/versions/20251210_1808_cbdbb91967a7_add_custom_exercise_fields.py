"""add_custom_exercise_fields

Revision ID: cbdbb91967a7
Revises: 005_add_user_name
Create Date: 2025-12-10 18:08:41.043039

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "cbdbb91967a7"
down_revision = "005_add_user_name"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_custom column with default False
    op.add_column(
        "exercise",
        sa.Column("is_custom", sa.Boolean(), nullable=False, server_default="false")
    )

    # Add user_id column (nullable - null for global exercises)
    op.add_column(
        "exercise",
        sa.Column("user_id", UUID(as_uuid=True), nullable=True)
    )

    # Add foreign key constraint
    op.create_foreign_key(
        "fk_exercise_user_id",
        "exercise",
        "user",
        ["user_id"],
        ["id"]
    )

    # Drop existing unique constraint on name
    op.drop_constraint("exercise_name_key", "exercise", type_="unique")

    # Add new unique constraint for name + user_id combination
    op.create_unique_constraint(
        "uq_exercise_name_user",
        "exercise",
        ["name", "user_id"]
    )

    # Add index for custom exercises by user
    op.create_index(
        "idx_exercise_user_id",
        "exercise",
        ["user_id"],
        postgresql_where=sa.text("is_custom = true")
    )


def downgrade() -> None:
    # Drop index
    op.drop_index("idx_exercise_user_id", table_name="exercise")

    # Drop unique constraint
    op.drop_constraint("uq_exercise_name_user", "exercise", type_="unique")

    # Recreate original unique constraint on name
    op.create_unique_constraint("exercise_name_key", "exercise", ["name"])

    # Drop foreign key
    op.drop_constraint("fk_exercise_user_id", "exercise", type_="foreignkey")

    # Drop columns
    op.drop_column("exercise", "user_id")
    op.drop_column("exercise", "is_custom")
