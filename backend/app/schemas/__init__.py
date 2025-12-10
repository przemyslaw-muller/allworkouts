"""
Schemas package for AllWorkouts API.

This package contains Pydantic schemas organized by domain:
- base: Common schemas (APIResponse, ErrorDetail, PaginationInfo, etc.)
- auth: Authentication schemas
- user: User schemas
- equipment: Equipment schemas
- exercises: Exercise schemas
- workout_plans: Workout plan schemas
- workout_sessions: Workout session schemas
- personal_records: Personal record schemas
- stats: Statistics schemas
- import_logs: Workout import log schemas
"""

# Base schemas
# Auth schemas
from .auth import (
    AuthResponse,
    AuthTokens,
    AuthUserResponse,
    LoginRequest,
    RefreshResponse,
    RefreshTokenRequest,
    RegisterRequest,
)
from .base import (
    APIResponse,
    ErrorDetail,
    HealthResponse,
    PaginationInfo,
    TimestampSchema,
)

# Equipment schemas
from .equipment import (
    EquipmentBase,
    EquipmentBrief,
    EquipmentCreate,
    EquipmentListItem,
    EquipmentOwnershipRequest,
    EquipmentOwnershipResponse,
    EquipmentResponse,
)

# Exercise schemas
from .exercises import (
    ExerciseBase,
    ExerciseBrief,
    ExerciseCreate,
    ExerciseDetailResponse,
    ExerciseListItem,
    ExerciseListResponse,
    ExerciseResponse,
    ExerciseSubstituteItem,
    PersonalRecordBrief,
)

# Import log schemas
from .import_logs import (
    WorkoutImportLogBase,
    WorkoutImportLogCreate,
    WorkoutImportLogResponse,
)

# Personal record schemas
from .personal_records import (
    PersonalRecordBase,
    PersonalRecordCreateRequest,
    PersonalRecordCreateResponse,
    PersonalRecordExerciseInfo,
    PersonalRecordListItem,
    PersonalRecordListResponse,
    PersonalRecordResponse,
)

# Stats schemas
from .stats import (
    ExerciseHistoryResponse,
    ExerciseHistorySession,
    ExerciseHistorySet,
    MonthlyWorkoutCount,
    MuscleGroupTrainingCount,
    StatsOverviewResponse,
)

# User schemas
from .user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdateRequest,
)

# Workout plan schemas
from .workout_plans import (
    ParsedExerciseItem,
    ParsedExerciseMatch,
    ParsedWorkoutItem,
    ParsedWorkoutPlan,
    WorkoutBase,
    WorkoutBrief,
    WorkoutCreate,
    WorkoutCreateItem,
    WorkoutDetail,
    WorkoutExerciseBase,
    WorkoutExerciseCreate,
    WorkoutExerciseCreateItem,
    WorkoutExerciseDetail,
    WorkoutExerciseResponse,
    WorkoutPlanBase,
    WorkoutPlanBrief,
    WorkoutPlanCreate,
    WorkoutPlanCreateRequest,
    WorkoutPlanCreateResponse,
    WorkoutPlanDetailResponse,
    WorkoutPlanFromParsedRequest,
    WorkoutPlanListItem,
    WorkoutPlanListResponse,
    WorkoutPlanParseRequest,
    WorkoutPlanParseResponse,
    WorkoutPlanResponse,
    WorkoutPlanToggleActiveRequest,
    WorkoutPlanToggleActiveResponse,
    WorkoutPlanUpdateRequest,
    WorkoutPlanUpdateResponse,
    WorkoutResponse,
)

# Workout session schemas
from .workout_sessions import (
    CompleteSessionRequest,
    CompleteSessionResponse,
    ExerciseContextInfo,
    ExerciseSessionBase,
    ExerciseSessionCreate,
    ExerciseSessionDetail,
    ExerciseSessionResponse,
    ExerciseSessionSetDetail,
    ExerciseSetLogItem,
    LogExerciseRequest,
    LogExerciseResponse,
    NewPersonalRecordInfo,
    PlannedExerciseWithContext,
    RecentSessionInfo,
    RecentSetInfo,
    SkipSessionRequest,
    SkipSessionResponse,
    WorkoutSessionBase,
    WorkoutSessionCreate,
    WorkoutSessionDetailResponse,
    WorkoutSessionListItem,
    WorkoutSessionListResponse,
    WorkoutSessionResponse,
    WorkoutSessionStartRequest,
    WorkoutSessionStartResponse,
)

__all__ = [
    # Base
    "APIResponse",
    "ErrorDetail",
    "HealthResponse",
    "PaginationInfo",
    "TimestampSchema",
    # Auth
    "AuthResponse",
    "AuthTokens",
    "AuthUserResponse",
    "LoginRequest",
    "RefreshResponse",
    "RefreshTokenRequest",
    "RegisterRequest",
    # User
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdateRequest",
    # Equipment
    "EquipmentBase",
    "EquipmentBrief",
    "EquipmentCreate",
    "EquipmentListItem",
    "EquipmentOwnershipRequest",
    "EquipmentOwnershipResponse",
    "EquipmentResponse",
    # Exercises
    "ExerciseBase",
    "ExerciseBrief",
    "ExerciseCreate",
    "ExerciseDetailResponse",
    "ExerciseListItem",
    "ExerciseListResponse",
    "ExerciseResponse",
    "ExerciseSubstituteItem",
    "PersonalRecordBrief",
    # Workout plans
    "ParsedExerciseItem",
    "ParsedExerciseMatch",
    "ParsedWorkoutItem",
    "ParsedWorkoutPlan",
    "WorkoutBase",
    "WorkoutBrief",
    "WorkoutCreate",
    "WorkoutCreateItem",
    "WorkoutDetail",
    "WorkoutExerciseBase",
    "WorkoutExerciseCreate",
    "WorkoutExerciseCreateItem",
    "WorkoutExerciseDetail",
    "WorkoutExerciseResponse",
    "WorkoutPlanBase",
    "WorkoutPlanBrief",
    "WorkoutPlanCreate",
    "WorkoutPlanCreateRequest",
    "WorkoutPlanCreateResponse",
    "WorkoutPlanDetailResponse",
    "WorkoutPlanFromParsedRequest",
    "WorkoutPlanListItem",
    "WorkoutPlanListResponse",
    "WorkoutPlanParseRequest",
    "WorkoutPlanParseResponse",
    "WorkoutPlanResponse",
    "WorkoutPlanToggleActiveRequest",
    "WorkoutPlanToggleActiveResponse",
    "WorkoutPlanUpdateRequest",
    "WorkoutPlanUpdateResponse",
    "WorkoutResponse",
    # Workout sessions
    "CompleteSessionRequest",
    "CompleteSessionResponse",
    "ExerciseContextInfo",
    "ExerciseSessionBase",
    "ExerciseSessionCreate",
    "ExerciseSessionDetail",
    "ExerciseSessionResponse",
    "ExerciseSessionSetDetail",
    "ExerciseSetLogItem",
    "LogExerciseRequest",
    "LogExerciseResponse",
    "NewPersonalRecordInfo",
    "PlannedExerciseWithContext",
    "RecentSessionInfo",
    "RecentSetInfo",
    "SkipSessionRequest",
    "SkipSessionResponse",
    "WorkoutSessionBase",
    "WorkoutSessionCreate",
    "WorkoutSessionDetailResponse",
    "WorkoutSessionListItem",
    "WorkoutSessionListResponse",
    "WorkoutSessionResponse",
    "WorkoutSessionStartRequest",
    "WorkoutSessionStartResponse",
    # Personal records
    "PersonalRecordBase",
    "PersonalRecordCreateRequest",
    "PersonalRecordCreateResponse",
    "PersonalRecordExerciseInfo",
    "PersonalRecordListItem",
    "PersonalRecordListResponse",
    "PersonalRecordResponse",
    # Stats
    "ExerciseHistoryResponse",
    "ExerciseHistorySession",
    "ExerciseHistorySet",
    "MonthlyWorkoutCount",
    "MuscleGroupTrainingCount",
    "StatsOverviewResponse",
    # Import logs
    "WorkoutImportLogBase",
    "WorkoutImportLogCreate",
    "WorkoutImportLogResponse",
]
