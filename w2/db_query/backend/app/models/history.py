"""Query history Pydantic models."""

from datetime import datetime

from pydantic import Field

from app.models import CamelModel


class QueryHistoryItem(CamelModel):
    """Single query history item."""

    id: int
    database_name: str
    sql: str
    query_type: str  # "manual" | "natural"
    natural_prompt: str | None = None
    row_count: int
    execution_time_ms: int
    status: str  # "success" | "error"
    error_message: str | None = None
    executed_at: datetime


class QueryHistoryList(CamelModel):
    """List of query history items with pagination."""

    items: list[QueryHistoryItem]
    total: int
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
