"""
ETL service for data ingestion and processing.
"""

import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings


class ETLService:
    """Service for ETL operations."""
    
    def __init__(self):
        """Initialize ETL service."""
        self.aqi_api_key = settings.AQI_API_KEY
        self.weather_api_key = settings.WEATHER_API_KEY
    
    async def fetch_aqi(self, latitude: float, longitude: float) -> Optional[float]:
        """Fetch AQI data from external API."""
        if not self.aqi_api_key:
            # Return mock data for development
            return 50.0
        
        try:
            async with httpx.AsyncClient() as client:
                # Example API call (adjust based on actual API)
                response = await client.get(
                    f"https://api.waqi.info/feed/geo:{latitude};{longitude}/?token={self.aqi_api_key}"
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", {}).get("aqi", 50.0)
        except Exception:
            pass
        
        return None
    
    async def fetch_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict[str, float]]:
        """Fetch weather data from external API."""
        if not self.weather_api_key:
            # Return mock data for development
            return {"temperature": 20.0, "humidity": 60.0}
        
        try:
            async with httpx.AsyncClient() as client:
                # Example API call (adjust based on actual API)
                response = await client.get(
                    f"https://api.openweathermap.org/data/2.5/weather",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.weather_api_key,
                        "units": "metric"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    main = data.get("main", {})
                    return {
                        "temperature": main.get("temp", 20.0),
                        "humidity": main.get("humidity", 60.0)
                    }
        except Exception:
            pass
        
        return None
    
    async def process_observation(
        self,
        hospital_id: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """Process observation with external data."""
        aqi = await self.fetch_aqi(latitude, longitude)
        weather = await self.fetch_weather(latitude, longitude)
        
        return {
            "aqi": aqi or 50.0,
            "temperature": weather.get("temperature", 20.0) if weather else 20.0,
            "humidity": weather.get("humidity", 60.0) if weather else 60.0,
            "timestamp": datetime.utcnow().isoformat()
        }


