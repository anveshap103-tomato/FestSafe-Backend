"""
Event schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class EventBase(BaseModel):
    """Base event schema."""
    name: str
    event_type: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    start_ts: datetime
    end_ts: datetime
    expected_attendance: Optional[int] = None


class EventCreate(EventBase):
    """Schema for creating an event."""
    pass


class Event(EventBase):
    """Event response schema."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


