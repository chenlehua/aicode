"""Tag service."""

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.exceptions import TagNameExistsError, TagNotFoundError
from app.models import Tag, TicketTag
from app.schemas.tag import TagCreate, TagUpdate


def get_tags(db: Session) -> list[Tag]:
    """Get all tags with ticket count."""
    # Query tags with ticket count
    stmt = (
        select(Tag, func.count(TicketTag.tag_id).label("ticket_count"))
        .outerjoin(TicketTag, Tag.id == TicketTag.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )

    results = db.execute(stmt).all()

    tags = []
    for tag, ticket_count in results:
        tag.ticket_count = ticket_count
        tags.append(tag)

    return tags


def get_tag_by_id(db: Session, tag_id: UUID) -> Tag:
    """Get tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise TagNotFoundError(str(tag_id))
    return tag


def create_tag(db: Session, tag_data: TagCreate) -> Tag:
    """Create a new tag."""
    # Check if tag name already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        raise TagNameExistsError(tag_data.name)

    tag = Tag(**tag_data.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag_id: UUID, tag_data: TagUpdate) -> Tag:
    """Update a tag."""
    tag = get_tag_by_id(db, tag_id)

    # Check if new name conflicts with existing tag
    if tag_data.name != tag.name:
        existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
        if existing_tag:
            raise TagNameExistsError(tag_data.name)

    # Update tag fields
    for key, value in tag_data.model_dump().items():
        setattr(tag, key, value)

    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag_id: UUID) -> None:
    """Delete a tag."""
    tag = get_tag_by_id(db, tag_id)
    db.delete(tag)
    db.commit()
