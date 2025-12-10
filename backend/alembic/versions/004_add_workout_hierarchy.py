"""Add workout hierarchy (Plan -> Workouts -> Exercises)

Revision ID: 004_add_workout_hierarchy
Revises: 003_nullable_exercise_session_id
Create Date: 2025-01-10 00:00:00

This migration:
1. Creates the new 'workout' table (intermediate between plan and exercises)
2. Adds is_active column to workout_plan
3. Adds workout_id to workout_session
4. Migrates workout_exercise from workout_plan_id to workout_id
5. Migrates existing data by creating default workouts for each plan
"""

import uuid

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_add_workout_hierarchy"
down_revision = "003_nullable_exercise_session_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Step 1: Add is_active column to workout_plan
    op.add_column(
        "workout_plan",
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Step 2: Create the workout table
    op.create_table(
        "workout",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workout_plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("day_number", sa.Integer(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(["workout_plan_id"], ["workout_plan.id"]),
    )
    op.create_index("idx_workout_workout_plan_id", "workout", ["workout_plan_id"])
    op.create_index("idx_workout_order", "workout", ["workout_plan_id", "order_index"])

    # Step 3: Add workout_id column to workout_exercise (nullable initially for migration)
    op.add_column(
        "workout_exercise",
        sa.Column("workout_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Step 4: Add workout_id column to workout_session (nullable initially for migration)
    op.add_column(
        "workout_session",
        sa.Column("workout_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Step 5: Create a default workout for each existing workout_plan and migrate data
    # This is done in raw SQL for performance
    op.execute("""
        -- Create a default workout for each workout_plan that has exercises
        INSERT INTO workout (id, workout_plan_id, name, day_number, order_index, created_at, updated_at)
        SELECT 
            gen_random_uuid(),
            wp.id,
            wp.name,
            1,
            0,
            wp.created_at,
            wp.updated_at
        FROM workout_plan wp
        WHERE EXISTS (
            SELECT 1 FROM workout_exercise we WHERE we.workout_plan_id = wp.id
        );
    """)

    # Step 6: Update workout_exercise to point to the new workout
    op.execute("""
        UPDATE workout_exercise we
        SET workout_id = w.id
        FROM workout w
        WHERE w.workout_plan_id = we.workout_plan_id;
    """)

    # Step 7: Update workout_session to point to the new workout
    op.execute("""
        UPDATE workout_session ws
        SET workout_id = w.id
        FROM workout w
        WHERE w.workout_plan_id = ws.workout_plan_id;
    """)

    # Step 8: For workout_sessions that don't have a corresponding workout, create one
    op.execute("""
        -- Create workouts for plans that have sessions but no exercises
        INSERT INTO workout (id, workout_plan_id, name, day_number, order_index, created_at, updated_at)
        SELECT 
            gen_random_uuid(),
            wp.id,
            wp.name,
            1,
            0,
            wp.created_at,
            wp.updated_at
        FROM workout_plan wp
        WHERE NOT EXISTS (
            SELECT 1 FROM workout w WHERE w.workout_plan_id = wp.id
        )
        AND EXISTS (
            SELECT 1 FROM workout_session ws WHERE ws.workout_plan_id = wp.id
        );
    """)

    # Step 9: Update any remaining workout_sessions
    op.execute("""
        UPDATE workout_session ws
        SET workout_id = w.id
        FROM workout w
        WHERE w.workout_plan_id = ws.workout_plan_id
        AND ws.workout_id IS NULL;
    """)

    # Step 10: Drop old constraints and indexes on workout_exercise
    op.drop_constraint(
        "workout_exercise_workout_plan_id_sequence_key", "workout_exercise", type_="unique"
    )
    op.drop_index("idx_workout_exercise_workout_plan_id", table_name="workout_exercise")
    op.drop_index("idx_workout_exercise_sequence", table_name="workout_exercise")
    op.drop_constraint(
        "workout_exercise_workout_plan_id_fkey", "workout_exercise", type_="foreignkey"
    )

    # Step 11: Make workout_id NOT NULL now that all data is migrated, and drop workout_plan_id
    op.alter_column("workout_exercise", "workout_id", nullable=False)
    op.drop_column("workout_exercise", "workout_plan_id")

    # Step 12: Add new constraints and indexes for workout_exercise
    op.create_foreign_key(
        "workout_exercise_workout_id_fkey",
        "workout_exercise",
        "workout",
        ["workout_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "workout_exercise_workout_id_sequence_key",
        "workout_exercise",
        ["workout_id", "sequence"],
    )
    op.create_index("idx_workout_exercise_workout_id", "workout_exercise", ["workout_id"])
    op.create_index("idx_workout_exercise_sequence", "workout_exercise", ["workout_id", "sequence"])

    # Step 13: Make workout_id NOT NULL for workout_session and add FK + index
    op.alter_column("workout_session", "workout_id", nullable=False)
    op.create_foreign_key(
        "workout_session_workout_id_fkey",
        "workout_session",
        "workout",
        ["workout_id"],
        ["id"],
    )
    op.create_index("idx_workout_session_workout_id", "workout_session", ["workout_id"])


def downgrade() -> None:
    # Step 1: Add workout_plan_id back to workout_exercise
    op.add_column(
        "workout_exercise",
        sa.Column("workout_plan_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # Step 2: Populate workout_plan_id from workout
    op.execute("""
        UPDATE workout_exercise we
        SET workout_plan_id = w.workout_plan_id
        FROM workout w
        WHERE w.id = we.workout_id;
    """)

    # Step 3: Drop new constraints and indexes on workout_exercise
    op.drop_index("idx_workout_exercise_sequence", table_name="workout_exercise")
    op.drop_index("idx_workout_exercise_workout_id", table_name="workout_exercise")
    op.drop_constraint(
        "workout_exercise_workout_id_sequence_key", "workout_exercise", type_="unique"
    )
    op.drop_constraint("workout_exercise_workout_id_fkey", "workout_exercise", type_="foreignkey")

    # Step 4: Make workout_plan_id NOT NULL and drop workout_id
    op.alter_column("workout_exercise", "workout_plan_id", nullable=False)
    op.drop_column("workout_exercise", "workout_id")

    # Step 5: Restore old constraints and indexes
    op.create_foreign_key(
        "workout_exercise_workout_plan_id_fkey",
        "workout_exercise",
        "workout_plan",
        ["workout_plan_id"],
        ["id"],
    )
    op.create_unique_constraint(
        "workout_exercise_workout_plan_id_sequence_key",
        "workout_exercise",
        ["workout_plan_id", "sequence"],
    )
    op.create_index("idx_workout_exercise_workout_plan_id", "workout_exercise", ["workout_plan_id"])
    op.create_index(
        "idx_workout_exercise_sequence",
        "workout_exercise",
        ["workout_plan_id", "sequence"],
    )

    # Step 6: Drop workout_id from workout_session
    op.drop_index("idx_workout_session_workout_id", table_name="workout_session")
    op.drop_constraint("workout_session_workout_id_fkey", "workout_session", type_="foreignkey")
    op.drop_column("workout_session", "workout_id")

    # Step 7: Drop workout table
    op.drop_index("idx_workout_order", table_name="workout")
    op.drop_index("idx_workout_workout_plan_id", table_name="workout")
    op.drop_table("workout")

    # Step 8: Drop is_active from workout_plan
    op.drop_column("workout_plan", "is_active")
