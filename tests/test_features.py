"""
Tests for feature modules.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.features.mitigation import recommend_mitigation, MitigationType
from src.features.historical import compare_to_historical, HISTORICAL_IMPACTS


class TestMitigation:
    """Test mitigation recommendations."""
    
    def test_low_risk_monitoring(self):
        """Low risk should recommend monitoring."""
        result = recommend_mitigation(
            diameter_m=50,
            risk_level="Low"
        )
        assert result.primary_method == MitigationType.MONITORING
    
    def test_high_risk_short_warning(self):
        """High risk with short warning should recommend nuclear."""
        result = recommend_mitigation(
            diameter_m=500,
            time_to_impact_days=90,
            risk_level="High"
        )
        assert result.primary_method == MitigationType.NUCLEAR_STANDOFF
    
    def test_medium_asteroid_long_warning(self):
        """Medium asteroid with long warning should use kinetic impactor."""
        result = recommend_mitigation(
            diameter_m=200,
            time_to_impact_days=2000,
            risk_level="High"
        )
        assert result.primary_method == MitigationType.KINETIC_IMPACTOR
    
    def test_small_asteroid_very_long_warning(self):
        """Small asteroid with very long warning could use gravity tractor."""
        result = recommend_mitigation(
            diameter_m=100,
            time_to_impact_days=3000,
            risk_level="High"
        )
        assert result.primary_method == MitigationType.GRAVITY_TRACTOR


class TestHistorical:
    """Test historical impact comparison."""
    
    def test_compare_small_asteroid(self):
        """Compare small asteroid to historical impacts."""
        result = compare_to_historical(
            diameter_m=20,
            velocity_kms=15,
            impact_probability=0.5
        )
        assert result["severity_class"] == "Minor"
        assert "nearest_analog" in result
    
    def test_compare_tunguska_size(self):
        """Compare Tunguska-sized asteroid."""
        result = compare_to_historical(
            diameter_m=50,
            velocity_kms=15,
            impact_probability=0.8
        )
        assert result["severity_class"] == "City Destroyer"
        assert result["size_comparison"]["vs_tunguska"] == 1.0
    
    def test_compare_large_asteroid(self):
        """Compare large asteroid."""
        result = compare_to_historical(
            diameter_m=500,
            velocity_kms=20,
            impact_probability=0.9
        )
        assert result["severity_class"] == "Global"
    
    def test_historical_impacts_exist(self):
        """Ensure historical impacts are populated."""
        assert len(HISTORICAL_IMPACTS) > 0
        assert any(i.name == "Chelyabinsk Meteor" for i in HISTORICAL_IMPACTS)
        assert any(i.name == "Tunguska Event" for i in HISTORICAL_IMPACTS)
