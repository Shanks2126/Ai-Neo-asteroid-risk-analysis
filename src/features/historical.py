"""
Historical impact data for comparison and context.
Contains data on significant historical asteroid/meteor impacts.
"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Dict


@dataclass
class HistoricalImpact:
    """Data on a historical asteroid/meteor impact."""
    name: str
    date: Optional[date]
    location: str
    diameter_m: float
    velocity_kms: float
    energy_mt: float  # Energy in megatons of TNT
    crater_diameter_km: float
    casualties: Optional[int]
    description: str
    

# Historical impacts database
HISTORICAL_IMPACTS: List[HistoricalImpact] = [
    HistoricalImpact(
        name="Chicxulub Impact",
        date=None,  # ~66 million years ago
        location="Yucatan Peninsula, Mexico",
        diameter_m=10000,  # ~10 km
        velocity_kms=20,
        energy_mt=100000000,  # 100 million megatons
        crater_diameter_km=180,
        casualties=None,  # Extinction event
        description="Caused the Cretaceous-Paleogene extinction event, killing ~75% of all species including non-avian dinosaurs."
    ),
    HistoricalImpact(
        name="Tunguska Event",
        date=date(1908, 6, 30),
        location="Siberia, Russia",
        diameter_m=50,  # 50-60 m estimate
        velocity_kms=15,
        energy_mt=10,  # 10-15 megatons
        crater_diameter_km=0,  # Air burst, no crater
        casualties=0,  # Remote area, possibly some reindeer herders
        description="Largest impact event in recorded history. Airburst flattened 2,000 km² of forest. No crater formed as object exploded in atmosphere."
    ),
    HistoricalImpact(
        name="Chelyabinsk Meteor",
        date=date(2013, 2, 15),
        location="Chelyabinsk Oblast, Russia",
        diameter_m=20,  # ~20 m
        velocity_kms=19,
        energy_mt=0.5,  # ~500 kilotons
        crater_diameter_km=0,  # Air burst
        casualties=0,  # 1,500 injured by shattered glass
        description="Brightest superbolide since Tunguska. Injured ~1,500 people, mostly from broken glass. Reminder that small asteroids can cause significant damage."
    ),
    HistoricalImpact(
        name="Barringer Crater",
        date=None,  # ~50,000 years ago
        location="Arizona, USA",
        diameter_m=50,
        velocity_kms=12,
        energy_mt=10,
        crater_diameter_km=1.2,
        casualties=None,
        description="Best-preserved impact crater on Earth. Also known as Meteor Crater. First crater recognized as meteoric origin."
    ),
    HistoricalImpact(
        name="Vredefort Crater",
        date=None,  # ~2 billion years ago
        location="South Africa",
        diameter_m=15000,  # ~15 km
        velocity_kms=20,
        energy_mt=500000000,  # 500 billion megatons
        crater_diameter_km=300,  # Original diameter
        casualties=None,
        description="Largest verified impact structure on Earth. UNESCO World Heritage Site."
    ),
    HistoricalImpact(
        name="Sudbury Basin",
        date=None,  # ~1.85 billion years ago
        location="Ontario, Canada",
        diameter_m=15000,
        velocity_kms=20,
        energy_mt=100000000,
        crater_diameter_km=130,
        casualties=None,
        description="One of the largest impact structures on Earth. Major source of nickel, copper, and platinum group metals."
    ),
]


def compare_to_historical(
    diameter_m: float,
    velocity_kms: float,
    impact_probability: float
) -> Dict:
    """
    Compare an asteroid to historical impacts.
    
    Args:
        diameter_m: Asteroid diameter in meters
        velocity_kms: Velocity in km/s
        impact_probability: Predicted impact probability
        
    Returns:
        Dict with comparison results and nearest historical analog
    """
    # Calculate approximate energy (very rough estimate)
    # E = 0.5 * m * v^2, assuming density of 3000 kg/m³
    mass_kg = (4/3) * 3.14159 * (diameter_m/2)**3 * 3000
    energy_joules = 0.5 * mass_kg * (velocity_kms * 1000)**2
    energy_mt = energy_joules / 4.184e15  # Convert to megatons TNT
    
    # Find nearest historical analog by diameter
    nearest = min(
        HISTORICAL_IMPACTS,
        key=lambda x: abs(x.diameter_m - diameter_m)
    )
    
    # Determine severity classification
    if diameter_m < 25:
        severity = "Minor"
        expected_damage = "Likely air burst. Possible broken windows, minor injuries in populated areas."
    elif diameter_m < 50:
        severity = "City Destroyer"  
        expected_damage = "Could devastate a metropolitan area. Similar to Tunguska event."
    elif diameter_m < 140:
        severity = "Regional"
        expected_damage = "Could destroy a region. Tsunamis if ocean impact."
    elif diameter_m < 300:
        severity = "Continental"
        expected_damage = "Continental-scale destruction. Global climate effects."
    elif diameter_m < 1000:
        severity = "Global"
        expected_damage = "Global catastrophe. Mass extinction possible."
    else:
        severity = "Extinction Level"
        expected_damage = "Similar to Chicxulub. Mass extinction event."
    
    return {
        "estimated_energy_mt": round(energy_mt, 2),
        "severity_class": severity,
        "expected_damage": expected_damage,
        "nearest_analog": {
            "name": nearest.name,
            "diameter_m": nearest.diameter_m,
            "energy_mt": nearest.energy_mt,
            "description": nearest.description
        },
        "size_comparison": {
            "vs_chelyabinsk": round(diameter_m / 20, 1),
            "vs_tunguska": round(diameter_m / 50, 1),
            "vs_chicxulub": round(diameter_m / 10000, 4)
        }
    }


def get_all_historical_impacts() -> List[Dict]:
    """Get all historical impacts as dictionaries."""
    return [
        {
            "name": impact.name,
            "date": impact.date.isoformat() if impact.date else "Prehistoric",
            "location": impact.location,
            "diameter_m": impact.diameter_m,
            "velocity_kms": impact.velocity_kms,
            "energy_mt": impact.energy_mt,
            "crater_diameter_km": impact.crater_diameter_km,
            "description": impact.description
        }
        for impact in HISTORICAL_IMPACTS
    ]
