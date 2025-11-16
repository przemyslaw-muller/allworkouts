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

# revision identifiers, used by Alembic.
revision = '002_seed_data'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Define table structures for bulk insert
    equipment_table = table(
        'equipment',
        column('id', postgresql.UUID),
        column('name', sa.String),
        column('description', sa.Text),
    )

    # Insert basic equipment
    equipment_data = [
        {'id': uuid.uuid4(), 'name': 'Bodyweight', 'description': 'No equipment required'},
        {'id': uuid.uuid4(), 'name': 'Barbell', 'description': 'Standard barbell'},
        {'id': uuid.uuid4(), 'name': 'Dumbbell', 'description': 'Dumbbells (pair)'},
        {'id': uuid.uuid4(), 'name': 'Pull-up Bar', 'description': 'Pull-up or chin-up bar'},
        {'id': uuid.uuid4(), 'name': 'Bench', 'description': 'Weight bench'},
        {'id': uuid.uuid4(), 'name': 'Squat Rack', 'description': 'Squat or power rack'},
        {'id': uuid.uuid4(), 'name': 'Cable Machine', 'description': 'Cable crossover or lat pulldown'},
        {'id': uuid.uuid4(), 'name': 'Resistance Bands', 'description': 'Elastic resistance bands'},
        {'id': uuid.uuid4(), 'name': 'Kettlebell', 'description': 'Kettlebell'},
        {'id': uuid.uuid4(), 'name': 'Medicine Ball', 'description': 'Weighted medicine ball'},
    ]

    op.bulk_insert(equipment_table, equipment_data)


def downgrade() -> None:
    # Remove seeded equipment
    op.execute("DELETE FROM equipment WHERE name IN ('Bodyweight', 'Barbell', 'Dumbbell', 'Pull-up Bar', 'Bench', 'Squat Rack', 'Cable Machine', 'Resistance Bands', 'Kettlebell', 'Medicine Ball')")
