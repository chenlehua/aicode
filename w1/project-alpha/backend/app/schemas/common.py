"""Common response schemas."""

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response model."""

    items: List[T]
    total: int
    page: int
    page_size: int


class SuccessResponse(BaseModel):
    """Success response model."""

    success: bool = True


class ErrorDetail(BaseModel):
    """Error detail model."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: ErrorDetail
