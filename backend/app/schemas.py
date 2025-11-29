from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator

from app.enums import (
    ConfidenceLevelEnum,
    MuscleGroupEnum,
    RecordTypeEnum,
    SessionStatusEnum,
    UnitSystemEnum,
)

# Generic type for API response data
T = TypeVar('T')


# Standard API Response Wrapper
class ErrorDetail(BaseModel):
    '''Error details for API responses'''

    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    '''Standard API response wrapper'''

    success: bool
    data: Optional[T] = None
    error: Optional[ErrorDetail] = None

    @classmethod
    def success_response(cls, data: T) -> 'APIResponse[T]':
        '''Create a successful response'''
        return cls(success=True, data=data, error=None)

    @classmethod
    def error_response(cls, code: str, message: str) -> 'APIResponse[Any]':
        '''Create an error response'''
        return cls(success=False, data=None, error=ErrorDetail(code=code, message=message))


# Base schemas for common fields
class TimestampSchema(BaseModel):
    '''Base schema with timestamp fields'''

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Authentication schemas
class RegisterRequest(BaseModel):
    '''Schema for user registration request'''

    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class LoginRequest(BaseModel):
    '''Schema for user login request'''

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    '''Schema for token refresh request'''

    refresh_token: str


class AuthUserResponse(BaseModel):
    '''User data returned in auth responses'''

    id: UUID
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuthTokens(BaseModel):
    '''Token pair for authentication'''

    access_token: str
    refresh_token: str


class AuthResponse(BaseModel):
    '''Response for login/register endpoints'''

    user: AuthUserResponse
    access_token: str
    refresh_token: str


class RefreshResponse(BaseModel):
    '''Response for token refresh endpoint'''

    access_token: str


# User schemas
class UserBase(BaseModel):
    '''Base user schema'''

    email: EmailStr
    unit_system: UnitSystemEnum = UnitSystemEnum.METRIC


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


class EquipmentListItem(BaseModel):
    '''Equipment item in list response with ownership status'''

    id: UUID
    name: str
    description: Optional[str] = None
    is_user_owned: bool = False

    class Config:
        from_attributes = True


class EquipmentOwnershipRequest(BaseModel):
    '''Request for updating equipment ownership'''

    is_owned: bool


class EquipmentOwnershipResponse(BaseModel):
    '''Response for equipment ownership update'''

    equipment_id: UUID
    is_owned: bool


# Pagination schema
class PaginationInfo(BaseModel):
    '''Pagination metadata'''

    page: int
    limit: int
    total: int
    total_pages: int


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


class EquipmentBrief(BaseModel):
    '''Brief equipment info for exercise list'''

    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ExerciseListItem(BaseModel):
    '''Exercise item in list response'''

    id: UUID
    name: str
    description: Optional[str] = None
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    equipment: list[EquipmentBrief] = []

    class Config:
        from_attributes = True


class ExerciseListResponse(BaseModel):
    '''Response for exercise list endpoint'''

    exercises: list[ExerciseListItem]
    pagination: PaginationInfo


class PersonalRecordBrief(BaseModel):
    '''Brief personal record info for exercise detail'''

    id: UUID
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = None
    achieved_at: datetime

    class Config:
        from_attributes = True


class ExerciseDetailResponse(BaseModel):
    '''Detailed exercise response with equipment and PRs'''

    id: UUID
    name: str
    description: Optional[str] = None
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    default_weight: Optional[Decimal] = None
    default_reps: Optional[int] = None
    default_rest_time_seconds: Optional[int] = None
    equipment: list[EquipmentBrief] = []
    personal_records: list[PersonalRecordBrief] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExerciseSubstituteItem(BaseModel):
    '''Exercise substitute suggestion'''

    id: UUID
    name: str
    description: Optional[str] = None
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    equipment: list[EquipmentBrief] = []
    match_score: float  # 0.0 to 1.0 based on muscle group overlap

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


# Workout Plan API schemas (for list/detail endpoints)
class ExerciseBrief(BaseModel):
    '''Brief exercise info for workout plan detail'''

    id: UUID
    name: str
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []

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


# =============================================================================
# Workout Session API schemas
# =============================================================================


class WorkoutPlanBrief(BaseModel):
    '''Brief workout plan info for session responses'''

    id: UUID
    name: str

    class Config:
        from_attributes = True


class WorkoutSessionListItem(BaseModel):
    '''Workout session item in list response'''

    id: UUID
    workout_plan: WorkoutPlanBrief
    status: SessionStatusEnum
    exercise_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorkoutSessionListResponse(BaseModel):
    '''Response for workout session list endpoint'''

    sessions: list[WorkoutSessionListItem]
    pagination: PaginationInfo


class ExerciseSessionSetDetail(BaseModel):
    '''Individual set within an exercise session'''

    id: UUID
    set_number: int
    weight: Decimal
    reps: int
    rest_time_seconds: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExerciseSessionDetail(BaseModel):
    '''Exercise session with all sets for session detail view'''

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
    '''Detailed workout session response with exercise sessions'''

    id: UUID
    workout_plan: WorkoutPlanBrief
    status: SessionStatusEnum
    exercise_sessions: list[ExerciseSessionDetail] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecentSetInfo(BaseModel):
    '''Recent set info for exercise context'''

    reps: int
    weight: Decimal

    class Config:
        from_attributes = True


class RecentSessionInfo(BaseModel):
    '''Recent session info for exercise context'''

    date: datetime
    sets: list[RecentSetInfo]

    class Config:
        from_attributes = True


class ExerciseContextInfo(BaseModel):
    '''Context info for an exercise (PR and recent sessions)'''

    personal_record: Optional[PersonalRecordBrief] = None
    recent_sessions: list[RecentSessionInfo] = []

    class Config:
        from_attributes = True


class PlannedExerciseWithContext(BaseModel):
    '''Planned exercise with historical context for session start'''

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
    '''Request for starting a workout session'''

    workout_plan_id: UUID


class WorkoutSessionStartResponse(BaseModel):
    '''Response for starting a workout session'''

    session_id: UUID
    workout_plan: WorkoutPlanBrief
    started_at: datetime
    exercises: list[PlannedExerciseWithContext]


class ExerciseSetLogItem(BaseModel):
    '''Individual set data for logging exercise'''

    set_number: int
    reps: int
    weight: Decimal
    rest_time_seconds: Optional[int] = None

    @field_validator('set_number')
    @classmethod
    def validate_set_number(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Set number must be at least 1')
        return v

    @field_validator('reps')
    @classmethod
    def validate_reps(cls, v: int) -> int:
        if v < 1:
            raise ValueError('Reps must be at least 1')
        return v

    @field_validator('weight')
    @classmethod
    def validate_weight(cls, v: Decimal) -> Decimal:
        if v < 0:
            raise ValueError('Weight must be non-negative')
        return v


class LogExerciseRequest(BaseModel):
    '''Request for logging an exercise during a session'''

    exercise_id: UUID
    sets: list[ExerciseSetLogItem]

    @field_validator('sets')
    @classmethod
    def validate_sets(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError('Must log at least 1 set')
        return v


class LogExerciseResponse(BaseModel):
    '''Response for logging an exercise'''

    exercise_session_ids: list[UUID]


class CompleteSessionRequest(BaseModel):
    '''Request for completing a session'''

    notes: Optional[str] = None


class NewPersonalRecordInfo(BaseModel):
    '''Info about a new personal record'''

    exercise_name: str
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = None


class CompleteSessionResponse(BaseModel):
    '''Response for completing a session'''

    session_id: UUID
    status: SessionStatusEnum
    duration_seconds: int
    new_personal_records: list[NewPersonalRecordInfo] = []


class SkipSessionRequest(BaseModel):
    '''Request for skipping a session'''

    notes: Optional[str] = None


class SkipSessionResponse(BaseModel):
    '''Response for skipping a session'''

    session_id: UUID
    status: SessionStatusEnum


# =============================================================================
# Personal Record API schemas
# =============================================================================


class PersonalRecordExerciseInfo(BaseModel):
    '''Exercise info for personal record response'''

    id: UUID
    name: str

    class Config:
        from_attributes = True


class PersonalRecordListItem(BaseModel):
    '''Personal record item in list response'''

    id: UUID
    exercise: PersonalRecordExerciseInfo
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = None
    achieved_at: datetime
    exercise_session_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class PersonalRecordListResponse(BaseModel):
    '''Response for personal record list endpoint'''

    records: list[PersonalRecordListItem]
    pagination: PaginationInfo


class PersonalRecordCreateRequest(BaseModel):
    '''Request for creating a personal record manually'''

    exercise_id: UUID
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = 'kg'
    achieved_at: Optional[datetime] = None
    notes: Optional[str] = None

    @field_validator('value')
    @classmethod
    def validate_value(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError('Value must be positive')
        return v

    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            valid_units = ['kg', 'lbs', 'seconds', 'meters']
            if v not in valid_units:
                raise ValueError(f'Unit must be one of: {", ".join(valid_units)}')
        return v


class PersonalRecordCreateResponse(BaseModel):
    '''Response for personal record creation'''

    id: UUID
    record_type: RecordTypeEnum
    value: Decimal


# =============================================================================
# Statistics API schemas
# =============================================================================


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


# Health check schema
class HealthResponse(BaseModel):
    '''Schema for health check response'''

    status: str
    timestamp: datetime
