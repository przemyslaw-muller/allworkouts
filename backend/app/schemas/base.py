from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel


# Generic type for API response data
T = TypeVar('T')


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


class TimestampSchema(BaseModel):
    '''Base schema with timestamp fields'''

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    '''Pagination metadata'''

    page: int
    limit: int
    total: int
    total_pages: int


class HealthResponse(BaseModel):
    '''Schema for health check response'''

    status: str
    timestamp: datetime
