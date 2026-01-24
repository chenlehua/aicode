"""Error codes and exception classes for pg-mcp."""

from enum import Enum


class ErrorCode(str, Enum):
    """Error codes for query operations."""

    SQL_GENERATION_FAILED = "SQL_GENERATION_FAILED"
    SQL_VALIDATION_FAILED = "SQL_VALIDATION_FAILED"
    SQL_UNSAFE = "SQL_UNSAFE"
    SQL_EXECUTION_FAILED = "SQL_EXECUTION_FAILED"
    SQL_TIMEOUT = "SQL_TIMEOUT"
    RESULT_VALIDATION_FAILED = "RESULT_VALIDATION_FAILED"
    DATABASE_CONNECTION_FAILED = "DATABASE_CONNECTION_FAILED"
    SCHEMA_NOT_FOUND = "SCHEMA_NOT_FOUND"
    LLM_API_ERROR = "LLM_API_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class QueryError(Exception):
    """Base exception class for query errors.

    Args:
        code: Error code identifying the error type.
        message: Human-readable error message.
        details: Additional error details (optional).
    """

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: str | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"[{self.code.value}] {self.message}: {self.details}"
        return f"[{self.code.value}] {self.message}"


class SQLGenerationError(QueryError):
    """Error raised when LLM fails to generate SQL."""

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(ErrorCode.SQL_GENERATION_FAILED, message, details)


class SQLUnsafeError(QueryError):
    """Error raised when SQL is deemed unsafe.

    Args:
        message: Description of why the SQL is unsafe.
        sql: The unsafe SQL statement (optional).
    """

    def __init__(self, message: str, sql: str | None = None) -> None:
        super().__init__(ErrorCode.SQL_UNSAFE, message, sql)
        self.sql = sql


class SQLExecutionError(QueryError):
    """Error raised when SQL execution fails.

    Args:
        message: Database error message.
        sql: The SQL statement that failed (optional).
    """

    def __init__(self, message: str, sql: str | None = None) -> None:
        super().__init__(ErrorCode.SQL_EXECUTION_FAILED, message, sql)
        self.sql = sql


class SQLTimeoutError(QueryError):
    """Error raised when SQL execution times out.

    Args:
        timeout_ms: The timeout value in milliseconds.
        sql: The SQL statement that timed out (optional).
    """

    def __init__(self, timeout_ms: int, sql: str | None = None) -> None:
        message = f"查询超时（超过 {timeout_ms}ms）"
        super().__init__(ErrorCode.SQL_TIMEOUT, message, sql)
        self.timeout_ms = timeout_ms
        self.sql = sql


class LLMError(QueryError):
    """Error raised when LLM API call fails.

    Args:
        message: Error message from the LLM API.
        details: Additional details (optional).
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        super().__init__(ErrorCode.LLM_API_ERROR, message, details)
