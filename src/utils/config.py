"""
Configuration management for NEO Risk API.
Uses pydantic-settings for environment variable management.
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    debug: bool = Field(default=False, description="Debug mode")
    
    # NASA API
    nasa_api_key: str = Field(default="DEMO_KEY", description="NASA API key")
    
    # Database
    database_url: str = Field(
        default="sqlite:///./neo_predictions.db",
        description="Database connection URL"
    )
    
    # Security
    secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key for JWT signing"
    )
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=100,
        description="API rate limit per minute"
    )
    
    # Alerts
    alert_webhook_url: str = Field(default="", description="Webhook URL for alerts")
    alert_email: str = Field(default="", description="Email for alerts")
    
    # Model Paths
    model_path: Path = Field(
        default=Path("models/risk_model.pkl"),
        description="Path to trained model"
    )
    scaler_path: Path = Field(
        default=Path("models/scaler.pkl"),
        description="Path to fitted scaler"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file on every request.
    """
    return Settings()


# Export settings instance for convenience
settings = get_settings()
