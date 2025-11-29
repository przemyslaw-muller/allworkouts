from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.enums import MuscleGroupEnum, RecordTypeEnum

from .base import PaginationInfo
from .equipment import EquipmentBrief


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


class ExerciseBrief(BaseModel):
    '''Brief exercise info for workout plan detail'''

    id: UUID
    name: str
    primary_muscle_groups: list[MuscleGroupEnum]
    secondary_muscle_groups: list[MuscleGroupEnum] = []

    class Config:
        from_attributes = True
