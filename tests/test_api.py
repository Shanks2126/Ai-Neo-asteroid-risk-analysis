"""
Tests for NEO Risk Prediction API.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.main import app


client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "model_loaded" in data


class TestPredictionEndpoints:
    """Test prediction endpoints."""
    
    def test_predict_low_risk(self):
        """Test prediction with low-risk parameters."""
        response = client.post("/predict", json={
            "distance_km": 9000000,
            "velocity_kms": 5,
            "diameter_m": 10,
            "trajectory_angle_deg": 85
        })
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "Low"
        assert 0 <= data["impact_probability"] <= 1
        assert "confidence" in data
    
    def test_predict_medium_risk(self):
        """Test prediction with medium-risk parameters."""
        response = client.post("/predict", json={
            "distance_km": 500000,
            "velocity_kms": 20,
            "diameter_m": 200,
            "trajectory_angle_deg": 45
        })
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] in ["Low", "Medium", "High"]
    
    def test_predict_high_risk(self):
        """Test prediction with high-risk parameters."""
        response = client.post("/predict", json={
            "distance_km": 50000,
            "velocity_kms": 40,
            "diameter_m": 900,
            "trajectory_angle_deg": 5
        })
        assert response.status_code == 200
        data = response.json()
        assert data["risk_level"] == "High"
    
    def test_predict_with_asteroid_name(self):
        """Test prediction with optional asteroid name."""
        response = client.post("/predict", json={
            "distance_km": 1000000,
            "velocity_kms": 15,
            "diameter_m": 100,
            "trajectory_angle_deg": 30,
            "asteroid_name": "2024 AB1"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["input_summary"]["asteroid_name"] == "2024 AB1"
    
    def test_predict_invalid_distance_zero(self):
        """Test that distance must be positive."""
        response = client.post("/predict", json={
            "distance_km": 0,
            "velocity_kms": 15,
            "diameter_m": 100,
            "trajectory_angle_deg": 30
        })
        assert response.status_code == 422  # Validation error
    
    def test_predict_invalid_distance_too_close(self):
        """Test that distance must be > 100km."""
        response = client.post("/predict", json={
            "distance_km": 50,
            "velocity_kms": 15,
            "diameter_m": 100,
            "trajectory_angle_deg": 30
        })
        assert response.status_code == 422
    
    def test_predict_invalid_velocity(self):
        """Test that velocity has upper limit."""
        response = client.post("/predict", json={
            "distance_km": 1000000,
            "velocity_kms": 100,  # Too fast
            "diameter_m": 100,
            "trajectory_angle_deg": 30
        })
        assert response.status_code == 422
    
    def test_predict_invalid_angle(self):
        """Test that angle must be 0-90."""
        response = client.post("/predict", json={
            "distance_km": 1000000,
            "velocity_kms": 15,
            "diameter_m": 100,
            "trajectory_angle_deg": 100  # Invalid
        })
        assert response.status_code == 422


class TestBatchPrediction:
    """Test batch prediction endpoint."""
    
    def test_batch_predict(self):
        """Test batch prediction with multiple asteroids."""
        response = client.post("/predict/batch", json={
            "asteroids": [
                {
                    "distance_km": 9000000,
                    "velocity_kms": 5,
                    "diameter_m": 10,
                    "trajectory_angle_deg": 85
                },
                {
                    "distance_km": 50000,
                    "velocity_kms": 40,
                    "diameter_m": 900,
                    "trajectory_angle_deg": 5
                }
            ]
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["predictions"]) == 2
        assert "processing_time_ms" in data
    
    def test_batch_empty(self):
        """Test batch with empty list."""
        response = client.post("/predict/batch", json={
            "asteroids": []
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0


class TestStatistics:
    """Test statistics endpoint."""
    
    def test_stats_endpoint(self):
        """Test statistics endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_predictions" in data
        assert "by_risk_level" in data


class TestHistory:
    """Test prediction history endpoint."""
    
    def test_history_default(self):
        """Test history with default parameters."""
        response = client.get("/predictions/history")
        assert response.status_code == 200
        data = response.json()
        assert "count" in data
        assert "predictions" in data
    
    def test_history_with_limit(self):
        """Test history with custom limit."""
        response = client.get("/predictions/history?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] <= 10
    
    def test_history_filter_by_risk(self):
        """Test history filtered by risk level."""
        response = client.get("/predictions/history?risk_level=High")
        assert response.status_code == 200
