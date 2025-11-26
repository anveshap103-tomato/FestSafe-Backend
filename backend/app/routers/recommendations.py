"""
Recommendations router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from app.db.database import get_db
from app.db import crud, models
from app.schemas import recommendation
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[recommendation.Recommendation])
async def get_recommendations(
    hospital_id: Optional[UUID] = None,
    event_id: Optional[UUID] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get recommendations with optional filters."""
    recommendations = crud.get_recommendations(
        db,
        hospital_id=hospital_id,
        event_id=event_id,
        status=status
    )
    return recommendations


@router.post("/", response_model=recommendation.Recommendation, status_code=status.HTTP_201_CREATED)
async def create_recommendation(
    recommendation_data: recommendation.RecommendationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new recommendation."""
    recommendation_dict = recommendation_data.model_dump()
    recommendation_dict["status"] = "proposed"
    
    return crud.create_recommendation(db, recommendation_dict)


@router.patch("/{recommendation_id}", response_model=recommendation.Recommendation)
async def update_recommendation(
    recommendation_id: UUID,
    update_data: recommendation.RecommendationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update recommendation status (approve/reject/modify)."""
    updated = crud.update_recommendation_status(
        db,
        recommendation_id=recommendation_id,
        status=update_data.status,
        reviewed_by=current_user.id
    )
    
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return updated


