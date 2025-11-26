"""
Hospitals router.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.database import get_db
from app.db import crud, models
from app.schemas import hospital
from app.core.security import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[hospital.Hospital])
async def get_hospitals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all hospitals."""
    hospitals = crud.get_hospitals(db, skip=skip, limit=limit)
    return hospitals


@router.get("/{hospital_id}", response_model=hospital.Hospital)
async def get_hospital(
    hospital_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific hospital."""
    hospital_obj = crud.get_hospital(db, hospital_id=hospital_id)
    if hospital_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    return hospital_obj


@router.post("/", response_model=hospital.Hospital, status_code=status.HTTP_201_CREATED)
async def create_hospital(
    hospital_data: hospital.HospitalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new hospital."""
    hospital_dict = hospital_data.model_dump()
    # Map schema fields to model fields
    hospital_dict["doctors_count"] = hospital_dict.get("doctors_count")
    hospital_dict["nurses_count"] = hospital_dict.get("nurses_count")
    
    return crud.create_hospital(db, hospital_dict)

