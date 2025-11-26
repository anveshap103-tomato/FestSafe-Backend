"""
CRUD operations for database models.
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.db import models


# Hospital CRUD
def get_hospital(db: Session, hospital_id: uuid.UUID) -> Optional[models.Hospital]:
    """Get hospital by ID."""
    return db.query(models.Hospital).filter(models.Hospital.id == hospital_id).first()


def get_hospitals(db: Session, skip: int = 0, limit: int = 100) -> List[models.Hospital]:
    """Get all hospitals."""
    return db.query(models.Hospital).offset(skip).limit(limit).all()


def create_hospital(db: Session, hospital_data: dict) -> models.Hospital:
    """Create a new hospital."""
    hospital = models.Hospital(**hospital_data)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


# Event CRUD
def get_event(db: Session, event_id: uuid.UUID) -> Optional[models.Event]:
    """Get event by ID."""
    return db.query(models.Event).filter(models.Event.id == event_id).first()


def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[models.Event]:
    """Get all events."""
    return db.query(models.Event).offset(skip).limit(limit).all()


def create_event(db: Session, event_data: dict) -> models.Event:
    """Create a new event."""
    event = models.Event(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# Observation CRUD
def get_observations(
    db: Session,
    hospital_id: Optional[uuid.UUID] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 1000
) -> List[models.Observation]:
    """Get observations with optional filters."""
    query = db.query(models.Observation)
    
    if hospital_id:
        query = query.filter(models.Observation.hospital_id == hospital_id)
    
    if start_time:
        query = query.filter(models.Observation.timestamp >= start_time)
    
    if end_time:
        query = query.filter(models.Observation.timestamp <= end_time)
    
    return query.order_by(desc(models.Observation.timestamp)).limit(limit).all()


def create_observation(db: Session, observation_data: dict) -> models.Observation:
    """Create a new observation."""
    observation = models.Observation(**observation_data)
    db.add(observation)
    db.commit()
    db.refresh(observation)
    return observation


# Forecast CRUD
def get_forecasts(
    db: Session,
    hospital_id: Optional[uuid.UUID] = None,
    event_id: Optional[uuid.UUID] = None,
    limit: int = 100
) -> List[models.Forecast]:
    """Get forecasts with optional filters."""
    query = db.query(models.Forecast)
    
    if hospital_id:
        query = query.filter(models.Forecast.hospital_id == hospital_id)
    
    if event_id:
        query = query.filter(models.Forecast.event_id == event_id)
    
    return query.order_by(desc(models.Forecast.forecast_timestamp)).limit(limit).all()


def create_forecast(db: Session, forecast_data: dict) -> models.Forecast:
    """Create a new forecast."""
    forecast = models.Forecast(**forecast_data)
    db.add(forecast)
    db.commit()
    db.refresh(forecast)
    return forecast


# Recommendation CRUD
def get_recommendations(
    db: Session,
    hospital_id: Optional[uuid.UUID] = None,
    event_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None
) -> List[models.Recommendation]:
    """Get recommendations with optional filters."""
    query = db.query(models.Recommendation)
    
    if hospital_id:
        query = query.filter(models.Recommendation.hospital_id == hospital_id)
    
    if event_id:
        query = query.filter(models.Recommendation.event_id == event_id)
    
    if status:
        query = query.filter(models.Recommendation.status == status)
    
    return query.order_by(desc(models.Recommendation.created_at)).all()


def create_recommendation(db: Session, recommendation_data: dict) -> models.Recommendation:
    """Create a new recommendation."""
    recommendation = models.Recommendation(**recommendation_data)
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation


def update_recommendation_status(
    db: Session,
    recommendation_id: uuid.UUID,
    status: str,
    reviewed_by: Optional[uuid.UUID] = None
) -> Optional[models.Recommendation]:
    """Update recommendation status."""
    recommendation = db.query(models.Recommendation).filter(
        models.Recommendation.id == recommendation_id
    ).first()
    
    if recommendation:
        recommendation.status = status
        recommendation.clinician_reviewed = True
        recommendation.reviewed_by = reviewed_by
        recommendation.reviewed_at = datetime.utcnow()
        db.commit()
        db.refresh(recommendation)
    
    return recommendation


# User CRUD
def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Get user by email."""
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user_data: dict) -> models.User:
    """Create a new user."""
    user = models.User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


