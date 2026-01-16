"""
Mitigation strategy recommendations based on asteroid parameters.
Suggests appropriate deflection methods based on size, time, and trajectory.
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class MitigationType(str, Enum):
    """Types of asteroid mitigation strategies."""
    KINETIC_IMPACTOR = "kinetic_impactor"
    GRAVITY_TRACTOR = "gravity_tractor"
    NUCLEAR_STANDOFF = "nuclear_standoff"
    ION_BEAM = "ion_beam"
    LASER_ABLATION = "laser_ablation"
    EVACUATION = "evacuation"
    MONITORING = "monitoring_only"


@dataclass
class MitigationStrategy:
    """Detailed mitigation strategy recommendation."""
    primary_method: MitigationType
    name: str
    description: str
    effectiveness: str  # Low, Medium, High
    time_required_days: int
    technology_readiness: str  # Proven, Experimental, Theoretical
    examples: List[str]
    considerations: List[str]


# Mitigation strategy database
STRATEGIES = {
    MitigationType.KINETIC_IMPACTOR: MitigationStrategy(
        primary_method=MitigationType.KINETIC_IMPACTOR,
        name="Kinetic Impactor",
        description="High-speed spacecraft collision to alter asteroid trajectory",
        effectiveness="High",
        time_required_days=365,
        technology_readiness="Proven",
        examples=["NASA DART mission (2022) - Successfully deflected Dimorphos"],
        considerations=[
            "Requires precise trajectory calculations",
            "Most effective for asteroids < 500m diameter",
            "Needs 1-10 years warning time",
            "May fragment rubble-pile asteroids"
        ]
    ),
    MitigationType.GRAVITY_TRACTOR: MitigationStrategy(
        primary_method=MitigationType.GRAVITY_TRACTOR,
        name="Gravity Tractor",
        description="Spacecraft hovers near asteroid, using gravitational pull to slowly alter course",
        effectiveness="Medium",
        time_required_days=1825,  # ~5 years
        technology_readiness="Experimental",
        examples=["Proposed for asteroid Apophis if needed"],
        considerations=[
            "Very slow but precise deflection",
            "Requires 10-20 years warning time",
            "Best for small asteroids < 200m",
            "No risk of fragmentation"
        ]
    ),
    MitigationType.NUCLEAR_STANDOFF: MitigationStrategy(
        primary_method=MitigationType.NUCLEAR_STANDOFF,
        name="Nuclear Standoff Detonation",
        description="Nuclear device exploded near asteroid surface to vaporize material and create thrust",
        effectiveness="Very High",
        time_required_days=180,
        technology_readiness="Theoretical",
        examples=["Last resort option, no missions tested"],
        considerations=[
            "Only for very large asteroids (> 500m) or short warning times",
            "International treaties may restrict use",
            "Risk of creating multiple fragments",
            "Most energy-efficient deflection method"
        ]
    ),
    MitigationType.ION_BEAM: MitigationStrategy(
        primary_method=MitigationType.ION_BEAM,
        name="Ion Beam Deflection",
        description="Spacecraft fires ion thrusters at asteroid surface to gradually push it",
        effectiveness="Medium",
        time_required_days=730,  # ~2 years
        technology_readiness="Experimental",
        examples=["Studied for ESA Hera mission follow-up"],
        considerations=[
            "Continuous propulsion required",
            "Works well for rotating asteroids",
            "Needs 5-10 years warning"
        ]
    ),
    MitigationType.LASER_ABLATION: MitigationStrategy(
        primary_method=MitigationType.LASER_ABLATION,
        name="Laser Ablation",
        description="Concentrated laser beams vaporize asteroid surface to create thrust",
        effectiveness="Low",
        time_required_days=1095,  # ~3 years
        technology_readiness="Theoretical",
        examples=["DE-STAR concept studies"],
        considerations=[
            "Requires significant power generation",
            "Distance-limited effectiveness",
            "Best for small, close asteroids"
        ]
    ),
    MitigationType.EVACUATION: MitigationStrategy(
        primary_method=MitigationType.EVACUATION,
        name="Civil Defense / Evacuation",
        description="Evacuate impact zone if deflection is not possible",
        effectiveness="Variable",
        time_required_days=30,
        technology_readiness="Proven",
        examples=["Standard disaster response protocols"],
        considerations=[
            "Last resort if deflection fails",
            "Effectiveness depends on impact size and location",
            "May be only option for very short warning times"
        ]
    ),
    MitigationType.MONITORING: MitigationStrategy(
        primary_method=MitigationType.MONITORING,
        name="Continued Monitoring",
        description="Object poses low risk, continue tracking and observation",
        effectiveness="N/A",
        time_required_days=0,
        technology_readiness="Proven",
        examples=["Standard protocol for most detected NEOs"],
        considerations=[
            "Appropriate for Low or Medium risk objects",
            "Allows time for more precise trajectory calculations",
            "May upgrade to active mitigation if risk increases"
        ]
    )
}


def recommend_mitigation(
    diameter_m: float,
    time_to_impact_days: Optional[float] = None,
    risk_level: str = "Low",
    velocity_kms: float = 15.0
) -> MitigationStrategy:
    """
    Recommend mitigation strategy based on asteroid parameters.
    
    Args:
        diameter_m: Asteroid diameter in meters
        time_to_impact_days: Days until potential impact (None = unknown)
        risk_level: Predicted risk level
        velocity_kms: Relative velocity in km/s
        
    Returns:
        Recommended MitigationStrategy
    """
    # Low risk - just monitor
    if risk_level == "Low":
        return STRATEGIES[MitigationType.MONITORING]
    
    # No warning time known - assume we have time
    if time_to_impact_days is None:
        time_to_impact_days = 3650  # Assume 10 years
    
    # Very short warning - emergency options only
    if time_to_impact_days < 180:
        if diameter_m > 300:
            return STRATEGIES[MitigationType.NUCLEAR_STANDOFF]
        else:
            return STRATEGIES[MitigationType.EVACUATION]
    
    # Short warning (6 months to 2 years)
    if time_to_impact_days < 730:
        if diameter_m > 500:
            return STRATEGIES[MitigationType.NUCLEAR_STANDOFF]
        else:
            return STRATEGIES[MitigationType.KINETIC_IMPACTOR]
    
    # Medium warning (2-5 years)
    if time_to_impact_days < 1825:
        if diameter_m < 200:
            return STRATEGIES[MitigationType.KINETIC_IMPACTOR]
        elif diameter_m < 500:
            return STRATEGIES[MitigationType.KINETIC_IMPACTOR]
        else:
            return STRATEGIES[MitigationType.NUCLEAR_STANDOFF]
    
    # Long warning (5+ years)
    if diameter_m < 150:
        return STRATEGIES[MitigationType.GRAVITY_TRACTOR]
    elif diameter_m < 300:
        return STRATEGIES[MitigationType.KINETIC_IMPACTOR]
    elif diameter_m < 500:
        return STRATEGIES[MitigationType.KINETIC_IMPACTOR]
    else:
        # Very large asteroid - may need multiple kinetic impactors
        return STRATEGIES[MitigationType.KINETIC_IMPACTOR]


def get_all_strategies() -> List[MitigationStrategy]:
    """Get all available mitigation strategies."""
    return list(STRATEGIES.values())
