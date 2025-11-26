"""
Application configuration.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str = "postgresql://festsafe:festsafe@localhost:5432/festsafe"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # ML Service
    ML_SERVICE_URL: str = "http://localhost:8001"
    
    # External APIs
    AQI_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    
    # Model
    MODEL_PATH: str = "models/baseline_model.pkl"
    MODEL_TYPE: str = "tabular"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


