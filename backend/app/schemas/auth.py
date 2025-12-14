from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    """Schema for user registration request"""

    email: EmailStr
    password: str
    name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_length(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (len(v) < 1 or len(v) > 100):
            raise ValueError("Name must be between 1 and 100 characters")
        return v


class LoginRequest(BaseModel):
    """Schema for user login request"""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request"""

    refresh_token: str


class AuthUserResponse(BaseModel):
    """User data returned in auth responses"""

    id: UUID
    email: str
    name: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthTokens(BaseModel):
    """Token pair for authentication"""

    access_token: str
    refresh_token: str


class AuthResponse(BaseModel):
    """Response for login/register endpoints"""

    user: AuthUserResponse
    access_token: str
    refresh_token: str


class RefreshResponse(BaseModel):
    """Response for token refresh endpoint"""

    access_token: str
