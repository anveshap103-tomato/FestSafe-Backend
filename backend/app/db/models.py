"""
Database models.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(String, default="HospitalOps")  # Admin, HospitalOps, PublicHealth
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Hospital(Base):
    """Hospital model."""
    __tablename__ = "hospitals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    bed_count = Column(Integer, nullable=False)
    icu_count = Column(Integer, nullable=False)
    oxygen_capacity = Column(Integer)  # liters
    doctors_count = Column(Integer)
    nurses_count = Column(Integer)
    contact_phone_hash = Column(String)  # Anonymized
    contact_email_hash = Column(String)  # Anonymized
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    observations = relationship("Observation", back_populates="hospital")
    recommendations = relationship("Recommendation", back_populates="hospital")


class Event(Base):
    """Event model."""
    __tablename__ = "events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    event_type = Column(String)  # Festival, Concert, Marathon, etc.
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    start_ts = Column(DateTime(timezone=True), nullable=False)
    end_ts = Column(DateTime(timezone=True), nullable=False)
    expected_attendance = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Observation(Base):
    """Time-series observation model."""
    __tablename__ = "observations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    current_patients = Column(Integer)
    new_arrivals = Column(Integer)
    avg_age = Column(Float)
    primary_complaint_codes = Column(JSON)  # List of ICD-10 codes
    aqi = Column(Float)  # Air Quality Index
    temperature = Column(Float)
    humidity = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="observations")


class Forecast(Base):
    """Forecast model."""
    __tablename__ = "forecasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    forecast_timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    forecast_horizon = Column(Integer)  # hours ahead
    predicted_arrivals = Column(Float)
    confidence = Column(Float)
    risk_category = Column(String)  # low, medium, high
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    """Resource recommendation model."""
    __tablename__ = "recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"), nullable=False, index=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    recommended_staffing = Column(JSON)  # {doctors: X, nurses: Y}
    recommended_supplies = Column(JSON)  # {oxygen: X, beds: Y}
    confidence = Column(Float)
    status = Column(String, default="proposed")  # proposed, approved, rejected, modified
    clinician_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    hospital = relationship("Hospital", back_populates="recommendations")


class AgentAction(Base):
    """Agent action log."""
    __tablename__ = "agent_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_type = Column(String)  # forecast, triage, communication
    observation = Column(JSON)
    action = Column(JSON)
    reasoning_trace = Column(JSON)
    confidence = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


