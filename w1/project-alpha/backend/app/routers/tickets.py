"""Ticket routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.schemas.ticket import (
    AddTagsRequest,
    RemoveTagsRequest,
    Ticket,
    TicketCreate,
    TicketFilters,
    TicketUpdate,
)
from app.services.ticket_service import (
    add_tags_to_ticket,
    complete_ticket,
    create_ticket,
    delete_ticket,
    get_ticket_by_id,
    get_tickets,
    remove_tags_from_ticket,
    reopen_ticket,
    update_ticket,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=PaginatedResponse[Ticket])
def list_tickets(
    tag_ids: Optional[str] = Query(None, description="标签ID列表（逗号分隔）"),
    status: Optional[str] = Query(None, description="状态筛选：open/completed"),
    search: Optional[str] = Query(None, description="标题搜索"),
    sort_by: Optional[str] = Query("created_at", description="排序字段"),
    sort_order: Optional[str] = Query("desc", description="排序方向"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
):
    """Get tickets with filtering, searching, sorting, and pagination."""
    # Parse tag_ids from comma-separated string
    tag_id_list = None
    if tag_ids:
        try:
            tag_id_list = [UUID(tid.strip()) for tid in tag_ids.split(",")]
        except ValueError:
            tag_id_list = []

    filters = TicketFilters(
        tag_ids=tag_id_list,
        status=status,
        search=search,
        sort_by=sort_by or "created_at",
        sort_order=sort_order or "desc",
        page=page,
        page_size=page_size,
    )

    tickets, total = get_tickets(db, filters)

    return PaginatedResponse(
        items=tickets,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Get a ticket by ID."""
    return get_ticket_by_id(db, ticket_id)


@router.post("", response_model=Ticket, status_code=201)
def create_new_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    """Create a new ticket."""
    return create_ticket(db, ticket_data)


@router.put("/{ticket_id}", response_model=Ticket)
def update_existing_ticket(
    ticket_id: UUID,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
):
    """Update a ticket."""
    return update_ticket(db, ticket_id, ticket_data)


@router.delete("/{ticket_id}", response_model=SuccessResponse)
def delete_existing_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Delete a ticket."""
    delete_ticket(db, ticket_id)
    return SuccessResponse()


@router.patch("/{ticket_id}/complete", response_model=Ticket)
def complete_ticket_route(ticket_id: UUID, db: Session = Depends(get_db)):
    """Mark a ticket as completed."""
    return complete_ticket(db, ticket_id)


@router.patch("/{ticket_id}/reopen", response_model=Ticket)
def reopen_ticket_route(ticket_id: UUID, db: Session = Depends(get_db)):
    """Reopen a completed ticket."""
    return reopen_ticket(db, ticket_id)


@router.post("/{ticket_id}/tags", response_model=Ticket)
def add_tags_to_ticket_route(
    ticket_id: UUID,
    request: AddTagsRequest,
    db: Session = Depends(get_db),
):
    """Add tags to a ticket."""
    return add_tags_to_ticket(db, ticket_id, request.tag_ids)


@router.delete("/{ticket_id}/tags", response_model=Ticket)
def remove_tags_from_ticket_route(
    ticket_id: UUID,
    request: RemoveTagsRequest,
    db: Session = Depends(get_db),
):
    """Remove tags from a ticket."""
    return remove_tags_from_ticket(db, ticket_id, request.tag_ids)
