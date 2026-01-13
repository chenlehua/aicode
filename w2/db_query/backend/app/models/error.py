"""Error response models."""

from typing import Any

from app.models import CamelModel


class ErrorResponse(CamelModel):
    """Standard error response format."""

    error: str
    message: str
    details: dict[str, Any] | None = None
