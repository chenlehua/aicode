"""Query request/response models for pg-mcp."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for natural language query."""

    query: str = Field(
        min_length=1,
        max_length=4096,
        description="Natural language query description",
    )


class QueryResultData(BaseModel):
    """Query execution result data."""

    columns: list[str] = Field(description="Column names")
    rows: list[list[Any]] = Field(description="Query result rows")
    row_count: int = Field(ge=0, description="Number of rows returned")
    execution_time_ms: float = Field(ge=0, description="Query execution time in milliseconds")


class ValidationResult(BaseModel):
    """LLM validation result for query output."""

    passed: bool = Field(description="Whether the validation passed")
    message: str = Field(description="Validation message or explanation")


class QueryResponse(BaseModel):
    """Response model for query execution."""

    success: bool = Field(description="Whether the query was successful")
    sql: str | None = Field(default=None, description="Generated SQL statement")
    result: QueryResultData | None = Field(default=None, description="Query result data")
    validation: ValidationResult | None = Field(default=None, description="LLM validation result")
    error: str | None = Field(default=None, description="Error message if query failed")
    error_code: str | None = Field(default=None, description="Error code if query failed")
    generated_at: datetime = Field(default_factory=datetime.now, description="Response generation timestamp")
