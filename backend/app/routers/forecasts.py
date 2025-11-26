"""
Forecasts router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import crud, models
from app.schemas import forecast
from app.core.security import get_current_active_user
from app.services.forecast_service import ForecastService

router = APIRouter()


@router.get("/hospital/{hospital_id}", response_model=List[forecast.Forecast])
async def get_hospital_forecasts(
    hospital_id: UUID,
    window: str = "24h",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get forecasts for a hospital."""
    # Parse window (e.g., "24h", "6h", "1h")
    hours = int(window.rstrip("h"))
    
    forecasts = crud.get_forecasts(db, hospital_id=hospital_id)
    # Filter by window if needed
    return forecasts[:10]  # Return latest 10


@router.post("/hospital/{hospital_id}/predict", response_model=forecast.Forecast)
async def predict_hospital_surge(
    hospital_id: UUID,
    event_id: Optional[UUID] = None,
    window: str = "24h",
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Generate a forecast for a hospital."""
    # Get hospital
    hospital_obj = crud.get_hospital(db, hospital_id=hospital_id)
    if not hospital_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Get recent observations
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)
    observations = crud.get_observations(
        db,
        hospital_id=hospital_id,
        start_time=start_time,
        end_time=end_time,
        limit=24
    )
    
    if not observations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient observation data"
        )
    
    # Use forecast service
    forecast_service = ForecastService()
    forecast_result = forecast_service.predict(
        hospital=hospital_obj,
        observations=observations,
        event_id=event_id,
        horizon_hours=int(window.rstrip("h"))
    )
    
    # Save forecast
    forecast_data = {
        "hospital_id": hospital_id,
        "event_id": event_id,
        "forecast_horizon": int(window.rstrip("h")),
        "forecast_timestamp": datetime.utcnow(),
        "predicted_arrivals": forecast_result["predicted_arrivals"],
        "confidence": forecast_result["confidence"],
        "risk_category": forecast_result["risk_category"],
        "model_version": "1.0.0"
    }
    
    saved_forecast = crud.create_forecast(db, forecast_data)
    return saved_forecast


