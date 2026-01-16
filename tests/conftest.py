"""
Pytest configuration and fixtures.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def sample_low_risk_asteroid():
    """Sample low-risk asteroid data."""
    return {
        "distance_km": 9000000,
        "velocity_kms": 5,
        "diameter_m": 10,
        "trajectory_angle_deg": 85
    }


@pytest.fixture
def sample_high_risk_asteroid():
    """Sample high-risk asteroid data."""
    return {
        "distance_km": 50000,
        "velocity_kms": 40,
        "diameter_m": 900,
        "trajectory_angle_deg": 5
    }


@pytest.fixture
def sample_batch_asteroids():
    """Sample batch of asteroids."""
    return [
        {
            "distance_km": 9000000,
            "velocity_kms": 5,
            "diameter_m": 10,
            "trajectory_angle_deg": 85
        },
        {
            "distance_km": 500000,
            "velocity_kms": 20,
            "diameter_m": 200,
            "trajectory_angle_deg": 45
        },
        {
            "distance_km": 50000,
            "velocity_kms": 40,
            "diameter_m": 900,
            "trajectory_angle_deg": 5
        }
    ]
