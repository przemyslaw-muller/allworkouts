from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.enums import ConfidenceLevelEnum, MuscleGroupEnum

from .base import PaginationInfo
from .exercises import ExerciseBrief


class WorkoutPlanBase(BaseModel):
    """Base workout plan schema"""

    name: str
    description: Optional[str] = None


class WorkoutPlanCreate(WorkoutPlanBase):
    """Schema for workout plan creation"""

    pass


class WorkoutPlanResponse(WorkoutPlanBase):
    """Schema for workout plan response"""

    id: UUID
    user_id: UUID
    is_active: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Workout Schemas (intermediate level between Plan and Exercises)
# =============================================================================


class WorkoutBase(BaseModel):
    """Base workout schema"""

    name: str
    day_number: Optional[int] = None
    order_index: int = 0


class WorkoutCreate(WorkoutBase):
    """Schema for workout creation"""

    pass


class WorkoutResponse(WorkoutBase):
    """Schema for workout response"""

    id: UUID
    workout_plan_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutBrief(BaseModel):
    """Brief workout info for session responses"""

    id: UUID
    name: str
    day_number: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Workout Exercise Schemas
# =============================================================================


class SetConfig(BaseModel):
    """Configuration for a single set"""

    set_number: int
    reps_min: int
    reps_max: int

    @field_validator('set_number')
    @classmethod
    def validate_set_number(cls, v: int) -> int:
        if v < 1 or v > 50:
            raise ValueError('Set number must be between 1 and 50')
        return v

    @field_validator('reps_min', 'reps_max')
    @classmethod
    def validate_reps(cls, v: int) -> int:
        if v < 1 or v > 200:
            raise ValueError('Reps must be between 1 and 200')
        return v


class WorkoutExerciseBase(BaseModel):
    """Base workout exercise schema"""

    exercise_id: UUID
    sequence: int
    set_configurations: list[SetConfig]
    rest_time_seconds: Optional[int] = None
    confidence_level: ConfidenceLevelEnum = ConfidenceLevelEnum.MEDIUM


class WorkoutExerciseCreate(WorkoutExerciseBase):
    """Schema for workout exercise creation"""

    pass


class WorkoutExerciseResponse(WorkoutExerciseBase):
    """Schema for workout exercise response"""

    id: UUID
    workout_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseDetail(BaseModel):
    """Exercise details within a workout"""

    id: UUID
    exercise: ExerciseBrief
    sequence: int
    set_configurations: list[SetConfig]
    rest_time_seconds: Optional[int] = None
    confidence_level: ConfidenceLevelEnum

    model_config = ConfigDict(from_attributes=True)


class WorkoutExerciseCreateItem(BaseModel):
    """Exercise item for workout creation/update"""

    exercise_id: UUID
    sequence: int
    set_configurations: list[SetConfig]
    rest_time_seconds: Optional[int] = None
    confidence_level: ConfidenceLevelEnum = ConfidenceLevelEnum.MEDIUM

    @field_validator('set_configurations')
    @classmethod
    def validate_set_configurations(cls, v: list[SetConfig]) -> list[SetConfig]:
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Must have between 1 and 50 sets')
        # Validate set numbers are sequential
        for i, config in enumerate(v, start=1):
            if config.set_number != i:
                raise ValueError('Set numbers must be sequential starting from 1')
        return v

    @field_validator("rest_time_seconds")
    @classmethod
    def validate_rest_time(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 0 or v > 3600):
            raise ValueError("Rest time must be between 0 and 3600 seconds")
        return v

    @field_validator("sequence")
    @classmethod
    def validate_sequence(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Sequence must be non-negative")
        return v


# =============================================================================
# Workout Detail (with exercises nested)
# =============================================================================


class WorkoutDetail(BaseModel):
    """Workout details with exercises"""

    id: UUID
    name: str
    day_number: Optional[int] = None
    order_index: int
    exercises: list[WorkoutExerciseDetail] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutCreateItem(BaseModel):
    """Workout item for plan creation/update (with nested exercises)"""

    name: str
    day_number: Optional[int] = None
    order_index: int = 0
    exercises: list[WorkoutExerciseCreateItem] = []

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 1 or len(v) > 255:
            raise ValueError("Workout name must be between 1 and 255 characters")
        return v.strip()

    @field_validator("exercises")
    @classmethod
    def validate_exercises(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError("Workout must have at least 1 exercise")
        return v


# =============================================================================
# Workout Plan List and Detail Responses
# =============================================================================


class WorkoutPlanListItem(BaseModel):
    """Workout plan item in list response"""

    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool = False
    workout_count: int = 0
    exercise_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanListResponse(BaseModel):
    """Response for workout plan list endpoint"""

    plans: list[WorkoutPlanListItem]
    pagination: PaginationInfo


class WorkoutPlanDetailResponse(BaseModel):
    """Detailed workout plan response with workouts and exercises"""

    id: UUID
    name: str
    description: Optional[str] = None
    is_active: bool = False
    workouts: list[WorkoutDetail] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Workout Plan Create/Update Requests
# =============================================================================


class WorkoutPlanCreateRequest(BaseModel):
    """Request for creating a workout plan with nested workouts"""

    name: str
    description: Optional[str] = None
    workouts: list[WorkoutCreateItem]

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 1 or len(v) > 200:
            raise ValueError("Name must be between 1 and 200 characters")
        return v.strip()

    @field_validator("workouts")
    @classmethod
    def validate_workouts(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError("Workout plan must have at least 1 workout")
        return v


class WorkoutPlanCreateResponse(BaseModel):
    """Response for workout plan creation"""

    id: UUID
    name: str
    created_at: datetime


class WorkoutPlanUpdateRequest(BaseModel):
    """Request for updating a workout plan"""

    name: Optional[str] = None
    description: Optional[str] = None
    workouts: Optional[list[WorkoutCreateItem]] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if len(v.strip()) < 1 or len(v) > 200:
                raise ValueError("Name must be between 1 and 200 characters")
            return v.strip()
        return v

    @field_validator("workouts")
    @classmethod
    def validate_workouts(cls, v: Optional[list]) -> Optional[list]:
        if v is not None and len(v) < 1:
            raise ValueError("Workout plan must have at least 1 workout")
        return v


class WorkoutPlanUpdateResponse(BaseModel):
    """Response for workout plan update"""

    id: UUID
    updated_at: datetime


class WorkoutPlanBrief(BaseModel):
    """Brief workout plan info for session responses"""

    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanToggleActiveRequest(BaseModel):
    """Request to toggle active status of a workout plan"""

    is_active: bool


class WorkoutPlanToggleActiveResponse(BaseModel):
    """Response for toggling active status"""

    id: UUID
    is_active: bool
    updated_at: datetime


# =============================================================================
# Parser-related schemas
# =============================================================================


class ParsedExerciseMatch(BaseModel):
    """Matched exercise from database with confidence"""

    exercise_id: UUID
    exercise_name: str
    original_text: str
    confidence: float
    confidence_level: ConfidenceLevelEnum
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum]

    model_config = ConfigDict(from_attributes=True)


class ParsedExerciseItem(BaseModel):
    """Single parsed exercise with matching info"""

    matched_exercise: Optional[ParsedExerciseMatch] = None
    original_text: str
    set_configurations: list[SetConfig]
    rest_seconds: Optional[int] = None
    notes: Optional[str] = None
    sequence: int
    alternatives: list[ParsedExerciseMatch] = []


class ParsedWorkoutItem(BaseModel):
    """Single parsed workout (day) with exercises"""

    name: str
    day_number: Optional[int] = None
    order_index: int = 0
    exercises: list[ParsedExerciseItem] = []


class WorkoutPlanParseRequest(BaseModel):
    """Request for parsing workout plan text"""

    text: str

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Text must be at least 10 characters")
        if len(v) > 50000:
            raise ValueError("Text must be less than 50,000 characters")
        return v.strip()


class ParsedWorkoutPlan(BaseModel):
    """Parsed workout plan structure from text (nested workouts)"""

    name: str
    description: Optional[str] = None
    workouts: list[ParsedWorkoutItem]
    raw_text: str
    import_log_id: UUID


class WorkoutPlanParseResponse(BaseModel):
    """Response from parse endpoint"""

    parsed_plan: ParsedWorkoutPlan
    total_exercises: int
    high_confidence_count: int
    medium_confidence_count: int
    low_confidence_count: int
    unmatched_count: int


class WorkoutPlanFromParsedRequest(BaseModel):
    """Create workout plan from parsed data (Step 2)"""

    import_log_id: UUID
    name: str
    description: Optional[str] = None
    workouts: list[WorkoutCreateItem]

    @field_validator("workouts")
    @classmethod
    def validate_workouts(cls, v: list) -> list:
        if len(v) < 1:
            raise ValueError("Workout plan must have at least 1 workout")
        return v
