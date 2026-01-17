"""Database-related Pydantic models."""

from datetime import datetime

from pydantic import Field

from app.models import CamelModel


class DatabaseCreate(CamelModel):
    """Request model for creating/updating a database connection."""

    url: str = Field(..., pattern=r"^postgres(ql)?://.*")
    description: str = Field(default="", max_length=500)


class DatabaseResponse(CamelModel):
    """Response model for database connection."""

    name: str
    url: str
    description: str = ""
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
    created_at: datetime | None = None
    updated_at: datetime | None = None
    metadata: DatabaseMetadata
