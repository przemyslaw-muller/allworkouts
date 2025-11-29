from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.enums import RecordTypeEnum

from .base import PaginationInfo


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
