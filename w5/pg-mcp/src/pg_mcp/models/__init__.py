"""Data models for pg-mcp."""

from pg_mcp.models.errors import (
    ErrorCode,
    LLMError,
    QueryError,
    SQLExecutionError,
    SQLGenerationError,
    SQLTimeoutError,
    SQLUnsafeError,
)
from pg_mcp.models.query import (
    QueryRequest,
    QueryResponse,
    QueryResultData,
    ValidationResult,
)
from pg_mcp.models.schema import (
    ColumnInfo,
    ConstraintInfo,
    DatabaseSchema,
    EnumTypeInfo,
    ForeignKeyRelation,
    IndexInfo,
    TableInfo,
    ViewInfo,
)

__all__ = [
    # Errors
    "ErrorCode",
    "QueryError",
    "SQLGenerationError",
    "SQLUnsafeError",
    "SQLExecutionError",
    "SQLTimeoutError",
    "LLMError",
    # Query models
    "QueryRequest",
    "QueryResponse",
    "QueryResultData",
    "ValidationResult",
    # Schema models
    "ColumnInfo",
    "IndexInfo",
    "ConstraintInfo",
    "TableInfo",
    "ViewInfo",
    "EnumTypeInfo",
    "ForeignKeyRelation",
    "DatabaseSchema",
]
