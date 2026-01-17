"""Database-related Pydantic models."""

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator

from app.models import CamelModel


class DatabaseType(str, Enum):
    """Supported database types."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


def detect_database_type(url: str) -> DatabaseType:
    """Detect database type from connection URL."""
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return DatabaseType.POSTGRESQL
    elif url.startswith("mysql://") or url.startswith("mysql+aiomysql://"):
        return DatabaseType.MYSQL
    raise ValueError(f"Unsupported database URL scheme: {url}")


class DatabaseCreate(CamelModel):
    """Request model for creating/updating a database connection.

    Supported URL formats:
    - PostgreSQL: postgresql://user:password@host:port/database
                  postgres://user:password@host:port/database
    - MySQL: mysql://user:password@host:port/database
             mysql+aiomysql://user:password@host:port/database

    Examples:
    - postgresql://postgres:postgres@localhost:5432/testdb
    - mysql://mysql:mysql@localhost:3306/testdb
    """

    url: str = Field(...)
    description: str = Field(default="", max_length=500)

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate that URL is a supported database connection string."""
        valid_prefixes = (
            "postgresql://",
            "postgres://",
            "mysql://",
            "mysql+aiomysql://",
        )
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                "URL must start with postgresql://, postgres://, mysql://, or mysql+aiomysql://"
            )
        return v


class DatabaseResponse(CamelModel):
    """Response model for database connection."""

    name: str
    url: str
    description: str = ""
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    created_at: datetime
    updated_at: datetime


class ColumnMetadata(CamelModel):
    """Column metadata within a table/view."""

    name: str
    data_type: str
    is_nullable: bool
    default_value: str | None = None
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: str | None = None  # "table.column" format


class TableMetadata(CamelModel):
    """Table or view metadata."""

    table_name: str
    table_type: str  # "table" | "view"
    columns: list[ColumnMetadata]
    fetched_at: datetime


class DatabaseMetadata(CamelModel):
    """Aggregated database metadata."""

    database_name: str
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    tables: list[TableMetadata]
    views: list[TableMetadata]
    table_count: int
    view_count: int
    fetched_at: datetime


class DatabaseWithMetadata(CamelModel):
    """Database connection with its metadata."""

    name: str
    url: str
    description: str = ""
    database_type: DatabaseType = DatabaseType.POSTGRESQL
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: DatabaseMetadata
