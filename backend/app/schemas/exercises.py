from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.enums import MuscleGroupEnum, RecordTypeEnum

from .base import PaginationInfo
from .equipment import EquipmentBrief


class ExerciseBase(BaseModel):
    """Base exercise schema"""

    name: str = Field(..., min_length=1, max_length=255)
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    default_weight: Optional[Decimal] = None
    default_reps: Optional[int] = None
    default_rest_time_seconds: Optional[int] = None
    description: Optional[str] = None


class ExerciseCreate(ExerciseBase):
    """Schema for custom exercise creation"""

    equipment_ids: list[UUID] = []


class ExerciseUpdate(BaseModel):
    """Schema for custom exercise update"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    primary_muscle_groups: Optional[list[MuscleGroupEnum]] = None
    secondary_muscle_groups: Optional[list[MuscleGroupEnum]] = None
    default_weight: Optional[Decimal] = None
    default_reps: Optional[int] = None
    default_rest_time_seconds: Optional[int] = None
    description: Optional[str] = None
    equipment_ids: Optional[list[UUID]] = None


class ExerciseResponse(ExerciseBase):
    """Schema for exercise response"""

    id: UUID
    is_custom: bool = False
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseListItem(BaseModel):
    """Exercise item in list response"""

    id: UUID
    name: str
    description: Optional[str] = None
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    equipment: list[EquipmentBrief] = []
    is_custom: bool = False

    model_config = ConfigDict(from_attributes=True)


class ExerciseListResponse(BaseModel):
    """Response for exercise list endpoint"""

    exercises: list[ExerciseListItem]
    pagination: PaginationInfo


class PersonalRecordBrief(BaseModel):
    """Brief personal record info for exercise detail"""

    id: UUID
    record_type: RecordTypeEnum
    value: Decimal
    unit: Optional[str] = None
    achieved_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseDetailResponse(BaseModel):
    """Detailed exercise response with equipment and PRs"""

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
    is_custom: bool = False
    user_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExerciseSubstituteItem(BaseModel):
    """Exercise substitute suggestion"""

    id: UUID
    name: str
    description: Optional[str] = None
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []
    equipment: list[EquipmentBrief] = []
    match_score: float  # 0.0 to 1.0 based on muscle group overlap

    model_config = ConfigDict(from_attributes=True)


class ExerciseBrief(BaseModel):
    """Brief exercise info for workout plan detail"""

    id: UUID
    name: str
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []

    model_config = ConfigDict(from_attributes=True)
