from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.enums import UnitSystemEnum


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


class UserUpdateRequest(BaseModel):
    '''Schema for updating user profile'''

    unit_system: Optional[UnitSystemEnum] = None
