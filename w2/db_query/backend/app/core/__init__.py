"""Core module for database adapter infrastructure."""

from app.core.exceptions import (
    AuthenticationError,
    ConnectionError,
    DatabaseError,
    QueryExecutionError,
    QueryValidationError,
    UnsupportedDatabaseError,
)
from app.core.registry import DatabaseRegistry, detect_database_type
from app.core.types import (
    ConnectionProvider,
    DatabaseConfig,
    DatabaseType,
    MetadataProvider,
    QueryExecutor,
    SQLDialect,
    TypeMapper,
)

__all__ = [
    # Types
    "DatabaseType",
    "DatabaseConfig",
    "SQLDialect",
    "ConnectionProvider",
    "MetadataProvider",
    "QueryExecutor",
    "TypeMapper",
    # Registry
    "DatabaseRegistry",
    "detect_database_type",
    # Exceptions
    "DatabaseError",
    "ConnectionError",
    "AuthenticationError",
    "QueryValidationError",
    "QueryExecutionError",
    "UnsupportedDatabaseError",
]
