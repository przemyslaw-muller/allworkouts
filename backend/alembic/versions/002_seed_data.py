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


def upgrade() -> None:
    # Get the path to the backend directory
    backend_dir = Path(__file__).parent.parent.parent

    # Define table structures for bulk insert
    equipment_table = table(
        'equipment',
        column('id', postgresql.UUID),
        column('name', sa.String),
        column('description', sa.Text),
    )

    exercise_table = table(
        'exercise',
        column('id', postgresql.UUID),
        column('name', sa.String),
        column('primary_muscle_groups', postgresql.ARRAY(sa.String)),
        column('secondary_muscle_groups', postgresql.ARRAY(sa.String)),
        column('default_weight', sa.Numeric),
        column('default_reps', sa.Integer),
        column('default_rest_time_seconds', sa.Integer),
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
    exercise_equipment_relationships = []
    exercise_data = []

    for ex in exercise_data_raw:
        ex_id = uuid.uuid4()

        # Prepare exercise record
        exercise_data.append({
            'id': ex_id,
            'name': ex['name'],
            'primary_muscle_groups': ex['primary_muscle_groups'],
            'secondary_muscle_groups': ex['secondary_muscle_groups'],
            'default_weight': ex.get('default_weight'),
            'default_reps': ex.get('default_reps'),
            'default_rest_time_seconds': ex.get('default_rest_time_seconds'),
            'description': ex.get('description')
        })

        # Create exercise-equipment relationships
        for equipment_name in ex.get('equipment', []):
            if equipment_name in equipment_id_map:
                exercise_equipment_relationships.append({
                    'exercise_id': ex_id,
                    'equipment_id': equipment_id_map[equipment_name]
                })

    # Insert exercises
    op.bulk_insert(exercise_table, exercise_data)

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
