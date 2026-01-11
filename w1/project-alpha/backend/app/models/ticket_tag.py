"""Ticket-Tag association table."""

from sqlalchemy import Column, DateTime, ForeignKey, PrimaryKeyConstraint, func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base


class TicketTag(Base):
    """Association table for many-to-many relationship between tickets and tags."""

    __tablename__ = "ticket_tags"

    ticket_id = Column(
        UUID(as_uuid=True), ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Composite primary key
    __table_args__ = (PrimaryKeyConstraint("ticket_id", "tag_id"),)
