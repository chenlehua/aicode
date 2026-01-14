"""Query-related Pydantic models."""

from typing import Any

from pydantic import Field

from app.models import CamelModel


class QueryRequest(CamelModel):
    """Request model for executing a SQL query."""

    sql: str = Field(..., min_length=1)


class NaturalQueryRequest(CamelModel):
    """Request model for natural language query generation."""

    prompt: str = Field(..., min_length=1, max_length=1000)


class ColumnInfo(CamelModel):
    """Column information for query results."""

    name: str
    data_type: str


class QueryResult(CamelModel):
    """Response model for query execution results."""

    columns: list[ColumnInfo]
    rows: list[list[Any]]
    row_count: int
    truncated: bool
    execution_time_ms: int


class GeneratedSQL(CamelModel):
    """Response model for generated SQL from natural language."""

    sql: str
    explanation: str | None = None
