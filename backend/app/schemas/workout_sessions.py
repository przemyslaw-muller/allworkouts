from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.enums import RecordTypeEnum, SessionStatusEnum

from .base import PaginationInfo
from .exercises import ExerciseBrief, PersonalRecordBrief
from .workout_plans import WorkoutBrief, WorkoutPlanBrief


class WorkoutSessionBase(BaseModel):
    """Base workout session schema"""

    workout_plan_id: UUID
    workout_id: UUID
    status: SessionStatusEnum = SessionStatusEnum.IN_PROGRESS


class WorkoutSessionCreate(WorkoutSessionBase):
    """Schema for workout session creation"""

    pass


class WorkoutSessionResponse(WorkoutSessionBase):
    """Schema for workout session response"""

    id: UUID
    user_id: UUID
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExerciseSessionBase(BaseModel):
    """Base exercise session schema"""

    exercise_id: UUID
    weight: Decimal
    reps: int
    rest_time_seconds: Optional[int] = None
    set_number: int


class ExerciseSessionCreate(ExerciseSessionBase):
    """Schema for exercise session creation"""

    pass


class ExerciseSessionResponse(ExerciseSessionBase):
    """Schema for exercise session response"""

    id: UUID
    workout_session_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutSessionListItem(BaseModel):
    """Workout session item in list response"""

    id: UUID
    workout_plan: WorkoutPlanBrief
    workout: WorkoutBrief
    status: SessionStatusEnum
    exercise_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutSessionListResponse(BaseModel):
    """Response for workout session list endpoint"""

    sessions: list[WorkoutSessionListItem]
    pagination: PaginationInfo


class ExerciseSessionSetDetail(BaseModel):
    """Individual set within an exercise session"""

    id: UUID
    set_number: int
    weight: Decimal
    reps: int
    rest_time_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseSessionDetail(BaseModel):
    """Exercise session with all sets for session detail view"""

    id: UUID
    exercise: ExerciseBrief
    set_number: int
    weight: Decimal
    reps: int
    rest_time_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutSessionDetailResponse(BaseModel):
    """Detailed workout session response with exercise sessions"""

    id: UUID
    workout_plan: WorkoutPlanBrief
    workout: WorkoutBrief
    status: SessionStatusEnum
    exercise_sessions: list[ExerciseSessionDetail] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecentSetInfo(BaseModel):
    """Recent set info for exercise context"""

    reps: int
    weight: Decimal

    class Config:
        from_attributes = True


class RecentSessionInfo(BaseModel):
    """Recent session info for exercise context"""

    date: datetime
    sets: list[RecentSetInfo]

    class Config:
        from_attributes = True


class ExerciseContextInfo(BaseModel):
    """Context info for an exercise (PR and recent sessions)"""

    personal_record: Optional[PersonalRecordBrief] = None
    recent_sessions: list[RecentSessionInfo] = []

    class Config:
        from_attributes = True


class PlannedExerciseWithContext(BaseModel):
    """Planned exercise with historical context for session start"""

    planned_exercise_id: UUID
    exercise: ExerciseBrief
    planned_sets: int
    planned_reps_min: int
    planned_reps_max: int
    rest_seconds: Optional[int] = None
    context: ExerciseContextInfo

    class Config:
        from_attributes = True


class WorkoutSessionStartRequest(BaseModel):
    """Request for starting a workout session"""

    workout_id: UUID


class WorkoutSessionStartResponse(BaseModel):
    """Response for starting a workout session"""

    session_id: UUID
    workout_plan: WorkoutPlanBrief
    workout: WorkoutBrief
    started_at: datetime
    exercises: list[PlannedExerciseWithContext]


class ExerciseSetLogItem(BaseModel):
    """Individual set data for logging exercise"""

    set_number: int
    reps: int
    weight: Decimal
    rest_time_seconds: Optional[int] = None

    @field_validator("set_number")
    @classmethod
    def validate_set_number(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Set number must be at least 1")
        return v

    @field_validator("reps")
    @classmethod
    def validate_reps(cls, v: int) -> int:
        if v < 1:
            raise ValueError("Reps must be at least 1")
        return v

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError("Weight must be non-negative")
        return v


class LogExerciseRequest(BaseModel):
    """Request for logging an exercise during a session"""

    exercise_id: UUID
    sets: list[ExerciseSetLogItem]

    @field_validator("sets")
    @classmethod
    def validate_sets(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError("Must log at least 1 set")
        return v


class LogExerciseResponse(BaseModel):
    """Response for logging an exercise"""

    exercise_session_ids: list[UUID]


class CompleteSessionRequest(BaseModel):
    """Request for completing a session"""

    notes: Optional[str] = None


class NewPersonalRecordInfo(BaseModel):
    """Info about a new personal record"""

    exercise_name: str
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = None


class CompleteSessionResponse(BaseModel):
    """Response for completing a session"""

    session_id: UUID
    status: SessionStatusEnum
    duration_seconds: int
    new_personal_records: list[NewPersonalRecordInfo] = []


class SkipSessionRequest(BaseModel):
    """Request for skipping a session"""

    notes: Optional[str] = None


class SkipSessionResponse(BaseModel):
    """Response for skipping a session"""

    session_id: UUID
    status: SessionStatusEnum
