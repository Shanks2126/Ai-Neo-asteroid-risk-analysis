"""
NEO Risk Prediction API - Enhanced Version
Full-featured FastAPI application with validation, logging, and database integration.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

# Internal imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.utils.config import settings
from src.utils.logging import logger, log_prediction, log_api_request
from src.database.connection import init_db, get_db
from src.database.models import PredictionRecord


# -----------------------------
# PYDANTIC SCHEMAS
# -----------------------------

class AsteroidInput(BaseModel):
    """Input schema for asteroid risk prediction."""
    
    distance_km: float = Field(
        ..., 
        gt=0, 
        le=4e8,  # Up to Moon's distance
        description="Distance from Earth in kilometers (must be positive)"
    )
    velocity_kms: float = Field(
        ..., 
        gt=0, 
        le=72,  # Max possible asteroid velocity
        description="Velocity in km/s (typical range: 5-40 km/s)"
    )
    diameter_m: float = Field(
        ..., 
        gt=0, 
        le=1000000,  # Up to Ceres size
        description="Asteroid diameter in meters"
    )
    trajectory_angle_deg: float = Field(
        ..., 
        ge=0, 
        le=90,
        description="Trajectory angle (0°=direct hit, 90°=tangential)"
    )
    asteroid_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Optional name of the asteroid"
    )
    
    @field_validator('distance_km')
    @classmethod
    def validate_distance(cls, v):
        if v < 100:
            raise ValueError('Object too close - would be in atmosphere')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "distance_km": 500000,
                "velocity_kms": 15.5,
                "diameter_m": 150,
                "trajectory_angle_deg": 30,
                "asteroid_name": "2024 AB1"
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for risk prediction."""
    
    risk_level: str = Field(..., description="Risk level: Low, Medium, or High")
    impact_probability: float = Field(..., ge=0, le=1, description="Probability of impact (0-1)")
    confidence: float = Field(..., ge=0, le=1, description="Model confidence score")
    
    # Input echo for confirmation
    input_summary: dict = Field(..., description="Summary of input parameters")
    
    # Metadata
    predicted_at: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = Field(default="1.0.0")


class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions."""
    asteroids: List[AsteroidInput] = Field(..., max_length=100)


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions."""
    predictions: List[PredictionResponse]
    total_count: int
    high_risk_count: int
    processing_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    model_loaded: bool
    database_connected: bool
    version: str


# -----------------------------
# MODEL LOADING
# -----------------------------

def load_model():
    """Load the trained model and scaler with error handling."""
    model_path = Path(__file__).parent.parent / "model" / "risk_model.pkl"
    scaler_path = Path(__file__).parent.parent / "model" / "scaler.pkl"
    
    # Try default paths first, then config paths
    if not model_path.exists():
        model_path = settings.model_path
    if not scaler_path.exists():
        scaler_path = settings.scaler_path
    
    try:
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        logger.info(f"Model loaded from {model_path}")
        return model, scaler
    except FileNotFoundError:
        logger.warning(f"Model not found at {model_path}. Using mock model.")
        return None, None
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None, None


# Global model and scaler
model, scaler = None, None


# -----------------------------
# APP LIFECYCLE
# -----------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    global model, scaler
    
    # Startup
    logger.info("🚀 Starting NEO Risk Prediction API...")
    
    # Initialize database
    init_db()
    logger.info("✅ Database initialized")
    
    # Load model
    model, scaler = load_model()
    if model is not None:
        logger.info("✅ ML model loaded")
    else:
        logger.warning("⚠️ ML model not loaded - using fallback predictions")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down NEO Risk Prediction API...")


# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI(
    title="NEO Risk Prediction API",
    description="""
    🌍 **Near-Earth Object Risk Assessment API**
    
    Predicts asteroid collision risk using machine learning based on:
    - Distance from Earth
    - Relative velocity
    - Asteroid diameter
    - Trajectory angle
    
    Integrates with NASA's NEO database for real-time data.
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# REQUEST LOGGING MIDDLEWARE
# -----------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    
    log_api_request(
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms
    )
    
    return response


# -----------------------------
# UTILITY FUNCTIONS
# -----------------------------

def predict_risk_internal(
    distance_km: float,
    velocity_kms: float,
    diameter_m: float,
    trajectory_angle_deg: float
) -> tuple[str, float, float]:
    """
    Internal prediction function.
    
    Returns:
        Tuple of (risk_level, impact_probability, confidence)
    """
    global model, scaler
    
    if model is None or scaler is None:
        # Fallback: rule-based prediction
        # Normalize values for scoring
        distance_score = 1 - min(distance_km / 1e7, 1)  # Closer = higher score
        velocity_score = min(velocity_kms / 40, 1)  # Faster = higher score
        size_score = min(diameter_m / 1000, 1)  # Larger = higher score
        angle_score = 1 - (trajectory_angle_deg / 90)  # More direct = higher score
        
        risk_score = (
            0.4 * distance_score +
            0.3 * velocity_score +
            0.2 * size_score +
            0.1 * angle_score
        )
        
        if risk_score < 0.35:
            risk_level = "Low"
        elif risk_score < 0.65:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return risk_level, risk_score, 0.7  # Lower confidence for rule-based
    
    # ML prediction
    input_array = np.array([[distance_km, velocity_kms, diameter_m, trajectory_angle_deg]])
    input_scaled = scaler.transform(input_array)
    
    risk_prediction = model.predict(input_scaled)[0]
    risk_probabilities = model.predict_proba(input_scaled)[0]
    max_probability = float(np.max(risk_probabilities))
    
    return risk_prediction, max_probability, max_probability


# -----------------------------
# ENDPOINTS
# -----------------------------

@app.get("/", tags=["General"])
def home():
    """Root endpoint - API information."""
    return {
        "message": "🌍 NEO Risk Prediction API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
def health_check():
    """Health check endpoint for monitoring."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        model_loaded=model is not None,
        database_connected=True,  # Will fail on first request if DB issue
        version="2.0.0"
    )


@app.post("/predict", response_model=PredictionResponse, tags=["Predictions"])
def predict_risk(data: AsteroidInput, db: Session = Depends(get_db)):
    """
    Predict collision risk for an asteroid.
    
    - **distance_km**: Distance from Earth (must be > 100 km)
    - **velocity_kms**: Relative velocity (max 72 km/s)
    - **diameter_m**: Asteroid diameter
    - **trajectory_angle_deg**: 0° = direct collision course
    """
    try:
        risk_level, impact_probability, confidence = predict_risk_internal(
            data.distance_km,
            data.velocity_kms,
            data.diameter_m,
            data.trajectory_angle_deg
        )
        
        # Log the prediction
        log_prediction(
            data.distance_km,
            data.velocity_kms,
            data.diameter_m,
            data.trajectory_angle_deg,
            risk_level,
            impact_probability
        )
        
        # Store in database
        record = PredictionRecord(
            distance_km=data.distance_km,
            velocity_kms=data.velocity_kms,
            diameter_m=data.diameter_m,
            trajectory_angle_deg=data.trajectory_angle_deg,
            risk_level=risk_level,
            impact_probability=impact_probability,
            asteroid_name=data.asteroid_name,
            source="api"
        )
        db.add(record)
        db.commit()
        
        return PredictionResponse(
            risk_level=risk_level,
            impact_probability=round(impact_probability, 4),
            confidence=round(confidence, 4),
            input_summary={
                "distance_km": data.distance_km,
                "velocity_kms": data.velocity_kms,
                "diameter_m": data.diameter_m,
                "trajectory_angle_deg": data.trajectory_angle_deg,
                "asteroid_name": data.asteroid_name
            },
            predicted_at=datetime.utcnow(),
            model_version="2.0.0" if model else "rule-based"
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post("/predict/batch", response_model=BatchPredictionResponse, tags=["Predictions"])
def predict_batch(request: BatchPredictionRequest, db: Session = Depends(get_db)):
    """
    Batch prediction for multiple asteroids.
    
    Maximum 100 asteroids per request.
    """
    start_time = time.time()
    predictions = []
    high_risk_count = 0
    
    for asteroid in request.asteroids:
        risk_level, impact_probability, confidence = predict_risk_internal(
            asteroid.distance_km,
            asteroid.velocity_kms,
            asteroid.diameter_m,
            asteroid.trajectory_angle_deg
        )
        
        if risk_level == "High":
            high_risk_count += 1
        
        predictions.append(PredictionResponse(
            risk_level=risk_level,
            impact_probability=round(impact_probability, 4),
            confidence=round(confidence, 4),
            input_summary={
                "distance_km": asteroid.distance_km,
                "velocity_kms": asteroid.velocity_kms,
                "diameter_m": asteroid.diameter_m,
                "trajectory_angle_deg": asteroid.trajectory_angle_deg,
                "asteroid_name": asteroid.asteroid_name
            },
            predicted_at=datetime.utcnow(),
            model_version="2.0.0" if model else "rule-based"
        ))
    
    processing_time = (time.time() - start_time) * 1000
    
    return BatchPredictionResponse(
        predictions=predictions,
        total_count=len(predictions),
        high_risk_count=high_risk_count,
        processing_time_ms=round(processing_time, 2)
    )


@app.get("/predictions/history", tags=["Predictions"])
def get_prediction_history(
    limit: int = 50,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get prediction history.
    
    - **limit**: Number of records to return (max 100)
    - **risk_level**: Filter by risk level (Low, Medium, High)
    """
    query = db.query(PredictionRecord).order_by(PredictionRecord.timestamp.desc())
    
    if risk_level:
        query = query.filter(PredictionRecord.risk_level == risk_level)
    
    records = query.limit(min(limit, 100)).all()
    
    return {
        "count": len(records),
        "predictions": [
            {
                "id": r.id,
                "timestamp": r.timestamp,
                "risk_level": r.risk_level,
                "impact_probability": r.impact_probability,
                "distance_km": r.distance_km,
                "velocity_kms": r.velocity_kms,
                "diameter_m": r.diameter_m,
                "asteroid_name": r.asteroid_name
            }
            for r in records
        ]
    }


@app.delete("/predictions/{prediction_id}", tags=["Predictions"])
def delete_prediction(prediction_id: int, db: Session = Depends(get_db)):
    """
    Delete a prediction from history.
    
    - **prediction_id**: ID of the prediction to delete
    """
    record = db.query(PredictionRecord).filter(PredictionRecord.id == prediction_id).first()
    
    if not record:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    db.delete(record)
    db.commit()
    
    logger.info("prediction_deleted", prediction_id=prediction_id)
    
    return {"message": "Prediction deleted successfully", "id": prediction_id}


@app.delete("/predictions", tags=["Predictions"])
def clear_all_predictions(db: Session = Depends(get_db)):
    """
    Clear all prediction history.
    """
    count = db.query(PredictionRecord).delete()
    db.commit()
    
    logger.info("predictions_cleared", count=count)
    
    return {"message": f"Deleted {count} predictions", "count": count}


@app.get("/stats", tags=["Analytics"])
def get_stats(db: Session = Depends(get_db)):
    """Get prediction statistics."""
    from sqlalchemy import func
    
    total = db.query(func.count(PredictionRecord.id)).scalar()
    
    risk_counts = db.query(
        PredictionRecord.risk_level,
        func.count(PredictionRecord.id)
    ).group_by(PredictionRecord.risk_level).all()
    
    return {
        "total_predictions": total,
        "by_risk_level": {level: count for level, count in risk_counts},
        "last_updated": datetime.utcnow()
    }


# -----------------------------
# EXCEPTION HANDLERS
# -----------------------------

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "type": "validation_error"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )


# -----------------------------
# MAIN
# -----------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
