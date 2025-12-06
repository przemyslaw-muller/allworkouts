"""Seed reference data

Revision ID: 002_seed_data
Revises: 001_initial
Create Date: 2024-01-01 00:01:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import postgresql
import uuid
import json
import os
from pathlib import Path

# revision identifiers, used by Alembic.
revision = '002_seed_data'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def _format_array_for_postgres(values: list) -> str:
    """Format a list as a PostgreSQL array literal with proper enum casting."""
    if not values:
        return "'{}'::muscle_group_enum[]"
    formatted = ','.join(values)
    return f"ARRAY[{','.join(repr(v) for v in values)}]::muscle_group_enum[]"


def upgrade() -> None:
    # Get the path to the backend directory
    backend_dir = Path(__file__).parent.parent.parent

    # Define table structures for bulk insert (equipment only)
    equipment_table = table(
        'equipment',
        column('id', postgresql.UUID),
        column('name', sa.String),
        column('description', sa.Text),
    )

    exercise_equipment_table = table(
        'exercise_equipment',
        column('exercise_id', postgresql.UUID),
        column('equipment_id', postgresql.UUID),
    )

    # Load equipment data from JSON
    equipment_json_path = backend_dir / 'seed_equipment.json'
    with open(equipment_json_path, 'r') as f:
        equipment_data_raw = json.load(f)

    # Create equipment records with UUIDs and store name-to-id mapping
    equipment_id_map = {}
    equipment_data = []
    for eq in equipment_data_raw:
        eq_id = uuid.uuid4()
        equipment_id_map[eq['name']] = eq_id
        equipment_data.append({
            'id': eq_id,
            'name': eq['name'],
            'description': eq['description']
        })

    # Insert equipment
    op.bulk_insert(equipment_table, equipment_data)

    # Load exercise data from JSON
    exercise_json_path = backend_dir / 'seed_exercises.json'
    with open(exercise_json_path, 'r') as f:
        exercise_data_raw = json.load(f)

    # Create exercise records and track exercise-equipment relationships
    # Use raw SQL for exercises to handle enum array types properly
    exercise_equipment_relationships = []
    connection = op.get_bind()

    for ex in exercise_data_raw:
        ex_id = uuid.uuid4()

        # Format muscle groups as PostgreSQL array literals with enum casting
        primary_array = _format_array_for_postgres(ex['primary_muscle_groups'])
        secondary_array = _format_array_for_postgres(ex['secondary_muscle_groups'])

        # Handle optional fields
        default_weight = ex.get('default_weight')
        default_reps = ex.get('default_reps')
        default_rest_time = ex.get('default_rest_time_seconds')
        description = ex.get('description')

        # Build the insert statement with proper escaping
        sql = sa.text('''
            INSERT INTO exercise (id, name, primary_muscle_groups, secondary_muscle_groups,
                                  default_weight, default_reps, default_rest_time_seconds, description)
            VALUES (:id, :name, ''' + primary_array + ', ' + secondary_array + ''',
                    :default_weight, :default_reps, :default_rest_time_seconds, :description)
        ''')

        connection.execute(sql, {
            'id': str(ex_id),
            'name': ex['name'],
            'default_weight': default_weight,
            'default_reps': default_reps,
            'default_rest_time_seconds': default_rest_time,
            'description': description
        })

        # Create exercise-equipment relationships
        for equipment_name in ex.get('equipment', []):
            if equipment_name in equipment_id_map:
                exercise_equipment_relationships.append({
                    'exercise_id': ex_id,
                    'equipment_id': equipment_id_map[equipment_name]
                })

    # Insert exercise-equipment relationships
    if exercise_equipment_relationships:
        op.bulk_insert(exercise_equipment_table, exercise_equipment_relationships)


def downgrade() -> None:
    # Remove seeded data
    # First remove exercise_equipment relationships (foreign key constraint)
    op.execute("DELETE FROM exercise_equipment")

    # Then remove exercises
    op.execute("DELETE FROM exercise")

    # Finally remove equipment
    op.execute("DELETE FROM equipment")
