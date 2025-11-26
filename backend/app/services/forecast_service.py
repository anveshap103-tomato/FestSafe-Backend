"""
Forecast service for generating predictions.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta

# Add ml directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "ml" / "inference"))

from serve import get_inference_service
from app.db import models


class ForecastService:
    """Service for generating hospital forecasts."""
    
    def __init__(self):
        """Initialize forecast service."""
        self.inference_service = get_inference_service()
    
    def predict(
        self,
        hospital: models.Hospital,
        observations: List[models.Observation],
        event_id: Optional[str] = None,
        horizon_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate a forecast for a hospital.
        
        Args:
            hospital: Hospital model instance
            observations: List of recent observations
            event_id: Optional event ID
            horizon_hours: Forecast horizon in hours
        
        Returns:
            Dictionary with forecast results
        """
        # Prepare features from observations
        if len(observations) < 24:
            # Pad with zeros if insufficient data
            observations = list(observations) + [None] * (24 - len(observations))
        
        # Extract features
        features = []
        for obs in observations[-24:]:  # Last 24 hours
            if obs:
                feature_vector = [
                    obs.new_arrivals or 0,
                    obs.current_patients or 0,
                    obs.avg_age or 50.0,
                    obs.aqi or 50.0,
                    obs.temperature or 20.0,
                    obs.humidity or 50.0,
                    hospital.bed_count,
                    hospital.icu_count,
                    hospital.oxygen_capacity or 0,
                    hospital.doctors_count or 0,
                    hospital.nurses_count or 0,
                    0  # event_attendance placeholder
                ]
            else:
                # Zero padding
                feature_vector = [0.0] * 12
            features.append(feature_vector)
        
        # Convert to numpy array
        features_array = np.array([features], dtype=np.float32)
        
        # Get prediction
        prediction_result = self.inference_service.predict(features_array)
        predicted_arrivals = prediction_result["predictions"][0]
        confidence = prediction_result.get("confidence", [0.8])[0]
        
        # Determine risk category
        if predicted_arrivals < 5:
            risk_category = "low"
        elif predicted_arrivals < 15:
            risk_category = "medium"
        else:
            risk_category = "high"
        
        return {
            "predicted_arrivals": float(predicted_arrivals),
            "confidence": float(confidence),
            "risk_category": risk_category,
            "forecast_horizon": horizon_hours
        }


