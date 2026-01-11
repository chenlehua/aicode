"""Ticket schemas."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.tag import Tag


class TicketBase(BaseModel):
    """Base ticket schema."""

    title: str = Field(..., min_length=1, max_length=255, description="Ticket 标题")
    description: Optional[str] = Field(None, description="Ticket 描述")


class TicketCreate(TicketBase):
    """Ticket creation schema."""

    tag_ids: List[UUID] = Field(default_factory=list, description="关联的标签ID列表")


class TicketUpdate(TicketBase):
    """Ticket update schema."""

    tag_ids: List[UUID] = Field(default_factory=list, description="关联的标签ID列表")


class Ticket(TicketBase):
    """Ticket response schema."""

    id: UUID
    status: str
    completed_at: Optional[datetime] = None
    tags: List[Tag] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketFilters(BaseModel):
    """Ticket filters schema."""

    tag_ids: Optional[List[UUID]] = Field(None, description="按标签筛选（支持多个）")
    status: Optional[str] = Field(None, pattern="^(open|completed)$", description="按状态筛选")
    search: Optional[str] = Field(None, description="按标题搜索（模糊匹配）")
    sort_by: Optional[str] = Field(
        default="created_at",
        pattern="^(created_at|updated_at|completed_at|title)$",
        description="排序字段",
    )
    sort_order: Optional[str] = Field(
        default="desc", pattern="^(asc|desc)$", description="排序方向"
    )
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class AddTagsRequest(BaseModel):
    """Add tags to ticket request schema."""

    tag_ids: List[UUID] = Field(..., min_length=1, description="要添加的标签ID列表")


class RemoveTagsRequest(BaseModel):
    """Remove tags from ticket request schema."""

    tag_ids: List[UUID] = Field(..., min_length=1, description="要移除的标签ID列表")
