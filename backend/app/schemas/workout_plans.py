from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.enums import ConfidenceLevelEnum, MuscleGroupEnum

from .base import PaginationInfo
from .exercises import ExerciseBrief


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


class WorkoutExerciseDetail(BaseModel):
    '''Exercise details within a workout plan'''

    id: UUID
    exercise: ExerciseBrief
    sequence: int
    sets: int
    reps_min: int
    reps_max: int
    rest_time_seconds: Optional[int] = None
    confidence_level: ConfidenceLevelEnum

    class Config:
        from_attributes = True


class WorkoutPlanListItem(BaseModel):
    '''Workout plan item in list response'''

    id: UUID
    name: str
    description: Optional[str] = None
    exercise_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutPlanListResponse(BaseModel):
    '''Response for workout plan list endpoint'''

    plans: list[WorkoutPlanListItem]
    pagination: PaginationInfo


class WorkoutPlanDetailResponse(BaseModel):
    '''Detailed workout plan response with exercises'''

    id: UUID
    name: str
    description: Optional[str] = None
    exercises: list[WorkoutExerciseDetail] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutExerciseCreateItem(BaseModel):
    '''Exercise item for workout plan creation/update'''

    exercise_id: UUID
    sequence: int
    sets: int
    reps_min: int
    reps_max: int
    rest_time_seconds: Optional[int] = None
    confidence_level: ConfidenceLevelEnum = ConfidenceLevelEnum.MEDIUM

    @field_validator('sets')
    @classmethod
    def validate_sets(cls, v: int) -> int:
        if v < 1 or v > 50:
            raise ValueError('Sets must be between 1 and 50')
        return v

    @field_validator('reps_min', 'reps_max')
    @classmethod
    def validate_reps(cls, v: int) -> int:
        if v < 1 or v > 200:
            raise ValueError('Reps must be between 1 and 200')
        return v

    @field_validator('rest_time_seconds')
    @classmethod
    def validate_rest_time(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 0 or v > 3600):
            raise ValueError('Rest time must be between 0 and 3600 seconds')
        return v

    @field_validator('sequence')
    @classmethod
    def validate_sequence(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Sequence must be non-negative')
        return v


class WorkoutPlanCreateRequest(BaseModel):
    '''Request for creating a workout plan'''

    name: str
    description: Optional[str] = None
    exercises: list[WorkoutExerciseCreateItem]

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 1 or len(v) > 200:
            raise ValueError('Name must be between 1 and 200 characters')
        return v.strip()

    @field_validator('exercises')
    @classmethod
    def validate_exercises(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError('Workout plan must have at least 1 exercise')
        return v


class WorkoutPlanCreateResponse(BaseModel):
    '''Response for workout plan creation'''

    id: UUID
    name: str
    created_at: datetime


class WorkoutPlanUpdateRequest(BaseModel):
    '''Request for updating a workout plan'''

    name: Optional[str] = None
    description: Optional[str] = None
    exercises: Optional[list[WorkoutExerciseCreateItem]] = None

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) < 1 or len(v) > 200:
                raise ValueError('Name must be between 1 and 200 characters')
            return v.strip()
        return v

    @field_validator('exercises')
    @classmethod
    def validate_exercises(cls, v: Optional[list]) -> Optional[list]:
        if v is not None and len(v) < 1:
            raise ValueError('Workout plan must have at least 1 exercise')
        return v


class WorkoutPlanUpdateResponse(BaseModel):
    '''Response for workout plan update'''

    id: UUID
    updated_at: datetime


class WorkoutPlanBrief(BaseModel):
    '''Brief workout plan info for session responses'''

    id: UUID
    name: str

    class Config:
        from_attributes = True
