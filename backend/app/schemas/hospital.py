"""
Hospital schemas.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class HospitalBase(BaseModel):
    """Base hospital schema."""
    name: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    bed_count: int = Field(..., gt=0)
    icu_count: int = Field(..., ge=0)
    oxygen_capacity: Optional[int] = None
    doctors_count: Optional[int] = None
    nurses_count: Optional[int] = None


class HospitalCreate(HospitalBase):
    """Schema for creating a hospital."""
    pass


class HospitalUpdate(BaseModel):
    """Schema for updating a hospital."""
    name: Optional[str] = None
    bed_count: Optional[int] = None
    icu_count: Optional[int] = None
    oxygen_capacity: Optional[int] = None
    doctors_count: Optional[int] = None
    nurses_count: Optional[int] = None


class Hospital(HospitalBase):
    """Hospital response schema."""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


