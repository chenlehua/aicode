"""Ticket service."""

from uuid import UUID

from sqlalchemy import and_
from sqlalchemy.orm import Session, selectinload

from app.exceptions import TagNotFoundError, TicketNotFoundError
from app.models import Tag, Ticket, TicketTag
from app.schemas.ticket import TicketCreate, TicketFilters, TicketUpdate


def get_tickets(
    db: Session,
    filters: TicketFilters,
) -> tuple[list[Ticket], int]:
    """Get tickets with filtering, searching, sorting, and pagination."""
    query = db.query(Ticket).options(selectinload(Ticket.tags))

    # Filter by tag_ids (tickets that have ANY of the specified tags)
    if filters.tag_ids:
        query = query.join(TicketTag).filter(TicketTag.tag_id.in_(filters.tag_ids)).distinct()

    # Filter by status
    if filters.status:
        query = query.filter(Ticket.status == filters.status)

    # Search by title (case-insensitive)
    if filters.search:
        search_pattern = f"%{filters.search}%"
        query = query.filter(Ticket.title.ilike(search_pattern))

    # Get total count before pagination
    total = query.count()

    # Sorting
    sort_column = getattr(Ticket, filters.sort_by, Ticket.created_at)
    if filters.sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    offset = (filters.page - 1) * filters.page_size
    tickets = query.offset(offset).limit(filters.page_size).all()

    return tickets, total


def get_ticket_by_id(db: Session, ticket_id: UUID) -> Ticket:
    """Get ticket by ID."""
    ticket = (
        db.query(Ticket).options(selectinload(Ticket.tags)).filter(Ticket.id == ticket_id).first()
    )
    if not ticket:
        raise TicketNotFoundError(str(ticket_id))
    return ticket


def create_ticket(db: Session, ticket_data: TicketCreate) -> Ticket:
    """Create a new ticket."""
    # Validate tag IDs exist
    if ticket_data.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(ticket_data.tag_ids)).all()
        existing_tag_ids = {tag.id for tag in existing_tags}
        invalid_tag_ids = set(ticket_data.tag_ids) - existing_tag_ids
        if invalid_tag_ids:
            raise TagNotFoundError(str(list(invalid_tag_ids)[0]))

    # Create ticket
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status="open",
    )
    db.add(ticket)
    db.flush()  # Get ticket ID

    # Add tags
    if ticket_data.tag_ids:
        for tag_id in ticket_data.tag_ids:
            ticket_tag = TicketTag(ticket_id=ticket.id, tag_id=tag_id)
            db.add(ticket_tag)

    db.commit()
    db.refresh(ticket)

    # Reload with tags
    return get_ticket_by_id(db, ticket.id)


def update_ticket(db: Session, ticket_id: UUID, ticket_data: TicketUpdate) -> Ticket:
    """Update a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)

    # Validate tag IDs exist
    if ticket_data.tag_ids:
        existing_tags = db.query(Tag).filter(Tag.id.in_(ticket_data.tag_ids)).all()
        existing_tag_ids = {tag.id for tag in existing_tags}
        invalid_tag_ids = set(ticket_data.tag_ids) - existing_tag_ids
        if invalid_tag_ids:
            raise TagNotFoundError(str(list(invalid_tag_ids)[0]))

    # Update ticket fields
    ticket.title = ticket_data.title
    ticket.description = ticket_data.description

    # Update tags (replace all existing tags)
    # Delete existing associations
    db.query(TicketTag).filter(TicketTag.ticket_id == ticket_id).delete()

    # Add new associations
    if ticket_data.tag_ids:
        for tag_id in ticket_data.tag_ids:
            ticket_tag = TicketTag(ticket_id=ticket.id, tag_id=tag_id)
            db.add(ticket_tag)

    db.commit()
    db.refresh(ticket)

    # Reload with tags
    return get_ticket_by_id(db, ticket.id)


def delete_ticket(db: Session, ticket_id: UUID) -> None:
    """Delete a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)
    db.delete(ticket)
    db.commit()


def complete_ticket(db: Session, ticket_id: UUID) -> Ticket:
    """Mark ticket as completed."""
    ticket = get_ticket_by_id(db, ticket_id)
    ticket.status = "completed"
    db.commit()
    db.refresh(ticket)

    # Reload with tags
    return get_ticket_by_id(db, ticket.id)


def reopen_ticket(db: Session, ticket_id: UUID) -> Ticket:
    """Reopen a completed ticket."""
    ticket = get_ticket_by_id(db, ticket_id)
    ticket.status = "open"
    db.commit()
    db.refresh(ticket)

    # Reload with tags
    return get_ticket_by_id(db, ticket.id)


def add_tags_to_ticket(db: Session, ticket_id: UUID, tag_ids: list[UUID]) -> Ticket:
    """Add tags to a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)

    # Validate tag IDs exist
    existing_tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
    existing_tag_ids = {tag.id for tag in existing_tags}
    invalid_tag_ids = set(tag_ids) - existing_tag_ids
    if invalid_tag_ids:
        raise TagNotFoundError(str(list(invalid_tag_ids)[0]))

    # Get existing tag associations
    existing_associations = db.query(TicketTag).filter(TicketTag.ticket_id == ticket_id).all()
    existing_tag_ids_in_ticket = {assoc.tag_id for assoc in existing_associations}

    # Add new tags (ignore duplicates)
    for tag_id in tag_ids:
        if tag_id not in existing_tag_ids_in_ticket:
            ticket_tag = TicketTag(ticket_id=ticket.id, tag_id=tag_id)
            db.add(ticket_tag)

    db.commit()

    # Reload with tags
    return get_ticket_by_id(db, ticket.id)


def remove_tags_from_ticket(db: Session, ticket_id: UUID, tag_ids: list[UUID]) -> Ticket:
    """Remove tags from a ticket."""
    ticket = get_ticket_by_id(db, ticket_id)

    # Remove tag associations (ignore non-existent)
    db.query(TicketTag).filter(
        and_(TicketTag.ticket_id == ticket_id, TicketTag.tag_id.in_(tag_ids))
    ).delete()

    db.commit()

    # Reload with tags
    return get_ticket_by_id(db, ticket.id)
