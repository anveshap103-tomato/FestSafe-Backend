"""
Events router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db import crud, models
from app.schemas import event
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[event.Event])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all events."""
    events = crud.get_events(db, skip=skip, limit=limit)
    return events


@router.get("/{event_id}", response_model=event.Event)
async def get_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific event."""
    event_obj = crud.get_event(db, event_id=event_id)
    if event_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return event_obj


@router.post("/", response_model=event.Event, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: event.EventCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new event."""
    event_dict = event_data.model_dump()
    return crud.create_event(db, event_dict)

