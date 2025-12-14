from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from app.enums import UnitSystemEnum


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    name: Optional[str] = None
    unit_system: UnitSystemEnum = UnitSystemEnum.METRIC


class UserCreate(UserBase):
    """Schema for user creation"""

    password: str


class UserResponse(UserBase):
    """Schema for user response"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateRequest(BaseModel):
    """Schema for updating user profile"""

    name: Optional[str] = None
    unit_system: Optional[UnitSystemEnum] = None

    @field_validator("name")
    @classmethod
    def name_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) < 1 or len(v) > 100):
            raise ValueError("Name must be between 1 and 100 characters")
        return v
