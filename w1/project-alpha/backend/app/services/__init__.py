"""Services package."""

from app.services.tag_service import create_tag, delete_tag, get_tag_by_id, get_tags, update_tag
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

__all__ = [
    # Tag services
    "get_tags",
    "get_tag_by_id",
    "create_tag",
    "update_tag",
    "delete_tag",
    # Ticket services
    "get_tickets",
    "get_ticket_by_id",
    "create_ticket",
    "update_ticket",
    "delete_ticket",
    "complete_ticket",
    "reopen_ticket",
    "add_tags_to_ticket",
    "remove_tags_from_ticket",
]
