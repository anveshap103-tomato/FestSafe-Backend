"""
Recommendation schemas.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class RecommendationBase(BaseModel):
    """Base recommendation schema."""
    hospital_id: UUID
    event_id: Optional[UUID] = None
    recommended_staffing: Dict[str, int]
    recommended_supplies: Dict[str, Any]
    confidence: float


class RecommendationCreate(RecommendationBase):
    """Schema for creating a recommendation."""
    pass


class RecommendationUpdate(BaseModel):
    """Schema for updating a recommendation."""
    status: str  # proposed, approved, rejected, modified


class Recommendation(RecommendationBase):
    """Recommendation response schema."""
    id: UUID
    status: str
    clinician_reviewed: bool
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


