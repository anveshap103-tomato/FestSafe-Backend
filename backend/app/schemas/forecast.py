"""
Forecast schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ForecastBase(BaseModel):
    """Base forecast schema."""
    hospital_id: UUID
    event_id: Optional[UUID] = None
    forecast_horizon: int  # hours
    predicted_arrivals: float
    confidence: float
    risk_category: str  # low, medium, high


class ForecastCreate(ForecastBase):
    """Schema for creating a forecast."""
    model_version: Optional[str] = None


class Forecast(ForecastBase):
    """Forecast response schema."""
    id: UUID
    forecast_timestamp: datetime
    model_version: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


