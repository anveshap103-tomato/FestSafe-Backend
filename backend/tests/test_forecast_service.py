"""
Tests for forecast service.
"""

import pytest
from datetime import datetime, timedelta
from app.services.forecast_service import ForecastService
from app.db import models


def test_forecast_service_predict():
    """Test forecast service prediction."""
    service = ForecastService()
    
    # Create mock hospital
    hospital = models.Hospital(
        id="test-id",
        name="Test Hospital",
        latitude=37.7749,
        longitude=-122.4194,
        bed_count=100,
        icu_count=10,
        oxygen_capacity=500,
        doctors_count=20,
        nurses_count=50
    )
    
    # Create mock observations
    observations = []
    for i in range(24):
        obs = models.Observation(
            id=f"obs-{i}",
            hospital_id="test-id",
            timestamp=datetime.utcnow() - timedelta(hours=24-i),
            new_arrivals=5 + i % 3,
            current_patients=50 + i % 10,
            avg_age=45.0,
            aqi=50.0,
            temperature=20.0,
            humidity=60.0
        )
        observations.append(obs)
    
    # Make prediction
    result = service.predict(hospital, observations, horizon_hours=24)
    
    assert "predicted_arrivals" in result
    assert "confidence" in result
    assert "risk_category" in result
    assert result["risk_category"] in ["low", "medium", "high"]


