"""Tag routes."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import SuccessResponse
from app.schemas.tag import Tag, TagCreate, TagListResponse, TagUpdate
from app.services.tag_service import create_tag, delete_tag, get_tag_by_id, get_tags, update_tag

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=TagListResponse)
def list_tags(db: Session = Depends(get_db)):
    """Get all tags with ticket count."""
    tags = get_tags(db)
    return TagListResponse(items=tags)


@router.get("/{tag_id}", response_model=Tag)
def get_tag(tag_id: UUID, db: Session = Depends(get_db)):
    """Get a tag by ID."""
    return get_tag_by_id(db, tag_id)


@router.post("", response_model=Tag, status_code=201)
def create_new_tag(tag_data: TagCreate, db: Session = Depends(get_db)):
    """Create a new tag."""
    return create_tag(db, tag_data)


@router.put("/{tag_id}", response_model=Tag)
def update_existing_tag(
    tag_id: UUID,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
):
    """Update a tag."""
    return update_tag(db, tag_id, tag_data)


@router.delete("/{tag_id}", response_model=SuccessResponse)
def delete_existing_tag(tag_id: UUID, db: Session = Depends(get_db)):
    """Delete a tag."""
    delete_tag(db, tag_id)
    return SuccessResponse()
