"""Tag schemas."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Base tag schema."""

    name: str = Field(..., min_length=1, max_length=50, description="标签名称")
    color: str = Field(
        default="#6366f1", pattern="^#[0-9A-Fa-f]{6}$", description="标签颜色（HEX格式）"
    )


class TagCreate(TagBase):
    """Tag creation schema."""

    pass


class TagUpdate(TagBase):
    """Tag update schema."""

    pass


class Tag(TagBase):
    """Tag response schema."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    ticket_count: Optional[int] = None

    class Config:
        from_attributes = True


class TagListResponse(BaseModel):
    """Tag list response schema."""

    items: list[Tag]
