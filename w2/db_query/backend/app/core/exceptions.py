"""Unified exception hierarchy for database operations."""

from enum import Enum
from typing import Any


class ErrorCode(str, Enum):
    """Standard error codes for database operations."""

    # Connection errors
    CONNECTION_FAILED = "CONNECTION_FAILED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    POOL_EXHAUSTED = "POOL_EXHAUSTED"

    # Query errors
    INVALID_SQL = "INVALID_SQL"
    QUERY_EXECUTION_FAILED = "QUERY_EXECUTION_FAILED"
    QUERY_TIMEOUT = "QUERY_TIMEOUT"

    # Metadata errors
    METADATA_FETCH_FAILED = "METADATA_FETCH_FAILED"
    TABLE_NOT_FOUND = "TABLE_NOT_FOUND"

    # General errors
    UNSUPPORTED_DATABASE = "UNSUPPORTED_DATABASE"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class DatabaseError(Exception):
    """Base exception for all database operations."""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}
        self.cause = cause

    def to_dict(self) -> dict[str, Any]:
        """Convert to API error response format."""
        return {
            "error": self.code.value,
            "message": self.message,
            "details": self.details if self.details else None,
        }


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(ErrorCode.CONNECTION_FAILED, message, **kwargs)


class AuthenticationError(DatabaseError):
    """Raised when authentication fails."""

    def __init__(self, message: str, **kwargs: Any):
        super().__init__(ErrorCode.AUTHENTICATION_FAILED, message, **kwargs)


class QueryValidationError(DatabaseError):
    """Raised when SQL validation fails."""

    def __init__(self, message: str, sql: str | None = None, **kwargs: Any):
        details = {"sql": sql} if sql else {}
        super().__init__(ErrorCode.INVALID_SQL, message, details=details, **kwargs)


class QueryExecutionError(DatabaseError):
    """Raised when query execution fails."""

    def __init__(self, message: str, sql: str | None = None, **kwargs: Any):
        details = {"sql": sql} if sql else {}
        super().__init__(
            ErrorCode.QUERY_EXECUTION_FAILED, message, details=details, **kwargs
        )


class UnsupportedDatabaseError(DatabaseError):
    """Raised when database type is not supported."""

    def __init__(self, db_type: str):
        super().__init__(
            ErrorCode.UNSUPPORTED_DATABASE,
            f"Database type '{db_type}' is not supported",
            details={"database_type": db_type},
        )
