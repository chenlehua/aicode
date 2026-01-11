"""Schemas package."""

from app.schemas.common import ErrorDetail, ErrorResponse, PaginatedResponse, SuccessResponse
from app.schemas.tag import Tag, TagCreate, TagListResponse, TagUpdate
from app.schemas.ticket import (
    AddTagsRequest,
    RemoveTagsRequest,
    Ticket,
    TicketCreate,
    TicketFilters,
    TicketUpdate,
)

__all__ = [
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "ErrorDetail",
    "Tag",
    "TagCreate",
    "TagUpdate",
    "TagListResponse",
    "Ticket",
    "TicketCreate",
    "TicketUpdate",
    "TicketFilters",
    "AddTagsRequest",
    "RemoveTagsRequest",
]
