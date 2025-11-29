from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.enums import MuscleGroupEnum

from .personal_records import PersonalRecordExerciseInfo


class MonthlyWorkoutCount(BaseModel):
    '''Workout count for a month'''

    month: str  # Format: YYYY-MM
    count: int


class MuscleGroupTrainingCount(BaseModel):
    '''Training count for a muscle group'''

    muscle_group: MuscleGroupEnum
    session_count: int


class StatsOverviewResponse(BaseModel):
    '''Response for stats overview endpoint'''

    total_workouts: int
    total_duration_seconds: int
    total_volume_kg: Decimal
    workouts_by_month: list[MonthlyWorkoutCount]
    most_trained_muscle_groups: list[MuscleGroupTrainingCount]
    current_streak_days: int
    personal_records_count: int


class ExerciseHistorySet(BaseModel):
    '''Set info for exercise history'''

    reps: int
    weight: Decimal
    unit: str = 'kg'


class ExerciseHistorySession(BaseModel):
    '''Session info for exercise history'''

    date: datetime
    total_volume: Decimal
    total_reps: int
    max_weight: Decimal
    sets: list[ExerciseHistorySet]


class ExerciseHistoryResponse(BaseModel):
    '''Response for exercise history endpoint'''

    exercise: PersonalRecordExerciseInfo
    sessions: list[ExerciseHistorySession]
