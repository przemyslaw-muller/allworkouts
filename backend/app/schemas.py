from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.enums import (
    ConfidenceLevelEnum,
    MuscleGroupEnum,
    RecordTypeEnum,
    SessionStatusEnum,
    UnitSystemEnum,
)


# Base schemas for common fields
class TimestampSchema(BaseModel):
    '''Base schema with timestamp fields'''

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    '''Base user schema'''

    email: EmailStr
    unit_system: UnitSystemEnum


class UserCreate(UserBase):
    '''Schema for user creation'''

    password: str


class UserResponse(UserBase):
    '''Schema for user response'''

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Equipment schemas
class EquipmentBase(BaseModel):
    '''Base equipment schema'''

    name: str
    description: Optional[str] = None


class EquipmentCreate(EquipmentBase):
    '''Schema for equipment creation'''

    pass


class EquipmentResponse(EquipmentBase):
    '''Schema for equipment response'''

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Exercise schemas
class ExerciseBase(BaseModel):
    '''Base exercise schema'''

    name: str
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    default_weight: Optional[Decimal] = None
    default_reps: Optional[int] = None
    default_rest_time_seconds: Optional[int] = None
    description: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    '''Schema for exercise creation'''

    pass


class ExerciseResponse(ExerciseBase):
    '''Schema for exercise response'''

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workout Plan schemas
class WorkoutPlanBase(BaseModel):
    '''Base workout plan schema'''

    name: str
    description: Optional[str] = None


class WorkoutPlanCreate(WorkoutPlanBase):
    '''Schema for workout plan creation'''

    pass


class WorkoutPlanResponse(WorkoutPlanBase):
    '''Schema for workout plan response'''

    id: UUID
    user_id: UUID
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workout Exercise schemas
class WorkoutExerciseBase(BaseModel):
    '''Base workout exercise schema'''

    exercise_id: UUID
    sequence: int
    sets: int
    reps_min: int
    reps_max: int
    rest_time_seconds: Optional[int] = None
    confidence_level: ConfidenceLevelEnum = ConfidenceLevelEnum.MEDIUM


class WorkoutExerciseCreate(WorkoutExerciseBase):
    '''Schema for workout exercise creation'''

    pass


class WorkoutExerciseResponse(WorkoutExerciseBase):
    '''Schema for workout exercise response'''

    id: UUID
    workout_plan_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workout Session schemas
class WorkoutSessionBase(BaseModel):
    '''Base workout session schema'''

    workout_plan_id: UUID
    status: SessionStatusEnum = SessionStatusEnum.IN_PROGRESS


class WorkoutSessionCreate(WorkoutSessionBase):
    '''Schema for workout session creation'''

    pass


class WorkoutSessionResponse(WorkoutSessionBase):
    '''Schema for workout session response'''

    id: UUID
    user_id: UUID
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Exercise Session schemas
class ExerciseSessionBase(BaseModel):
    '''Base exercise session schema'''

    exercise_id: UUID
    weight: Decimal
    reps: int
    rest_time_seconds: Optional[int] = None
    set_number: int


class ExerciseSessionCreate(ExerciseSessionBase):
    '''Schema for exercise session creation'''

    pass


class ExerciseSessionResponse(ExerciseSessionBase):
    '''Schema for exercise session response'''

    id: UUID
    workout_session_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Personal Record schemas
class PersonalRecordBase(BaseModel):
    '''Base personal record schema'''

    exercise_id: UUID
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = None


class PersonalRecordResponse(PersonalRecordBase):
    '''Schema for personal record response'''

    id: UUID
    user_id: UUID
    exercise_session_id: UUID
    achieved_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Workout Import Log schemas
class WorkoutImportLogBase(BaseModel):
    '''Base workout import log schema'''

    raw_text: str
    workout_plan_id: Optional[UUID] = None


class WorkoutImportLogCreate(WorkoutImportLogBase):
    '''Schema for workout import log creation'''

    parsed_exercises: Optional[dict] = None
    confidence_scores: Optional[dict] = None


class WorkoutImportLogResponse(WorkoutImportLogBase):
    '''Schema for workout import log response'''

    id: UUID
    user_id: UUID
    parsed_exercises: Optional[dict] = None
    confidence_scores: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Health check schema
class HealthResponse(BaseModel):
    '''Schema for health check response'''

    status: str
    timestamp: datetime
