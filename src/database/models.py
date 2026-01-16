"""
SQLAlchemy database models for NEO Risk API.
Stores prediction history and asteroid data.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class PredictionRecord(Base):
    """
    Stores individual prediction requests and results.
    Used for analytics, auditing, and historical analysis.
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Input parameters
    distance_km = Column(Float, nullable=False)
    velocity_kms = Column(Float, nullable=False)
    diameter_m = Column(Float, nullable=False)
    trajectory_angle_deg = Column(Float, nullable=False)
    
    # Prediction results
    risk_level = Column(String(20), nullable=False, index=True)
    impact_probability = Column(Float, nullable=False)
    uncertainty = Column(Float, nullable=True)  # Model uncertainty
    
    # Metadata
    source = Column(String(50), default="api")  # api, nasa, batch
    asteroid_name = Column(String(100), nullable=True)
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, risk={self.risk_level}, prob={self.impact_probability:.3f})>"


class NASAAsteroid(Base):
    """
    Cached asteroid data from NASA NEO API.
    Reduces API calls and provides historical reference.
    """
    __tablename__ = "nasa_asteroids"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    neo_reference_id = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False)
    
    # Size estimates (in meters)
    diameter_min_m = Column(Float)
    diameter_max_m = Column(Float)
    diameter_avg_m = Column(Float)
    
    # Hazard classification
    is_potentially_hazardous = Column(Boolean, default=False)
    is_sentry_object = Column(Boolean, default=False)
    
    # Close approach data
    close_approach_date = Column(DateTime, index=True)
    miss_distance_km = Column(Float)
    relative_velocity_kms = Column(Float)
    
    # Our risk assessment
    calculated_risk_level = Column(String(20))
    calculated_impact_probability = Column(Float)
    
    # Metadata
    fetched_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(Text)  # Store raw JSON for debugging
    
    def __repr__(self):
        return f"<NASAAsteroid(name={self.name}, hazardous={self.is_potentially_hazardous})>"


class AlertRecord(Base):
    """
    Tracks sent alerts for high-risk predictions.
    Prevents duplicate alerts and provides audit trail.
    """
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Trigger details
    trigger_type = Column(String(50))  # prediction, nasa_update, threshold
    risk_level = Column(String(20))
    asteroid_name = Column(String(100), nullable=True)
    
    # Alert delivery
    channel = Column(String(50))  # email, webhook, sms
    recipient = Column(String(200))
    status = Column(String(20))  # sent, failed, pending
    
    # Message content (truncated)
    message_preview = Column(String(500))
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.trigger_type}, status={self.status})>"
