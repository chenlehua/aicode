"""Error response models."""

from enum import Enum
from typing import Any

from app.models import CamelModel


class ErrorCode(str, Enum):
    """Standard error codes for API responses."""

    # General errors
    INVALID_NAME = "INVALID_NAME"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"

    # Database connection errors
    CONNECTION_FAILED = "CONNECTION_FAILED"
    UNSUPPORTED_DATABASE = "UNSUPPORTED_DATABASE"

    # Metadata errors
    METADATA_FETCH_FAILED = "METADATA_FETCH_FAILED"

    # Query errors
    INVALID_SQL = "INVALID_SQL"
    QUERY_EXECUTION_FAILED = "QUERY_EXECUTION_FAILED"

    # LLM errors
    LLM_GENERATION_FAILED = "LLM_GENERATION_FAILED"
    LLM_SERVICE_ERROR = "LLM_SERVICE_ERROR"

    # MySQL-specific errors
    MYSQL_CONNECTION_ERROR = "MYSQL_CONNECTION_ERROR"
    MYSQL_AUTHENTICATION_ERROR = "MYSQL_AUTHENTICATION_ERROR"

    # PostgreSQL-specific errors
    POSTGRESQL_CONNECTION_ERROR = "POSTGRESQL_CONNECTION_ERROR"
    POSTGRESQL_AUTHENTICATION_ERROR = "POSTGRESQL_AUTHENTICATION_ERROR"


class ErrorResponse(CamelModel):
    """Standard error response format."""

    error: str
    message: str
    details: dict[str, Any] | None = None
