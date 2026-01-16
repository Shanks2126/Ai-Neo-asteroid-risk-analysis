"""
Orbital Mechanics Module for Accurate Asteroid Trajectory Calculation.

Implements Keplerian orbital mechanics to compute accurate asteroid positions
based on orbital elements (semi-major axis, eccentricity, inclination, etc.)

References:
- Orbital Mechanics for Engineering Students (Howard Curtis)
- JPL HORIZONS System: https://ssd.jpl.nasa.gov/horizons/
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import numpy as np


# Constants
AU_TO_KM = 149597870.7  # Astronomical Unit to kilometers
EARTH_ORBITAL_RADIUS = 1.0  # AU
GRAVITATIONAL_PARAM_SUN = 1.32712440018e11  # km³/s² (GM of Sun)
DEG_TO_RAD = math.pi / 180
RAD_TO_DEG = 180 / math.pi


@dataclass
class OrbitalElements:
    """
    Keplerian Orbital Elements for an asteroid.
    
    These 6 elements uniquely define an orbit in 3D space.
    """
    # Primary orbital elements
    semi_major_axis: float  # a - in AU (average distance from Sun)
    eccentricity: float     # e - shape of orbit (0=circle, <1=ellipse, 1=parabola)
    inclination: float      # i - tilt from ecliptic plane (degrees)
    
    # Orientation elements
    longitude_ascending_node: float  # Ω (Omega) - where orbit crosses ecliptic going up (degrees)
    argument_perihelion: float       # ω (omega) - angle from ascending node to perihelion (degrees)
    
    # Position element
    mean_anomaly: float     # M - position along orbit at epoch (degrees)
    
    # Reference time
    epoch: datetime         # t₀ - when these elements are valid
    
    # Optional identifiers
    name: Optional[str] = None
    neo_reference_id: Optional[str] = None
    
    # Physical properties
    diameter_m: Optional[float] = None
    absolute_magnitude: Optional[float] = None
    is_potentially_hazardous: bool = False


@dataclass 
class CartesianState:
    """
    Position and velocity in Cartesian coordinates.
    Uses heliocentric ecliptic coordinate system.
    """
    x: float  # km
    y: float  # km  
    z: float  # km
    vx: float = 0.0  # km/s
    vy: float = 0.0  # km/s
    vz: float = 0.0  # km/s
    
    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])
    
    def distance_from_origin(self) -> float:
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)


class OrbitalMechanics:
    """
    Core orbital mechanics calculations using Kepler's laws.
    """
    
    @staticmethod
    def solve_kepler_equation(M: float, e: float, tolerance: float = 1e-10, max_iter: int = 100) -> float:
        """
        Solve Kepler's equation: M = E - e*sin(E)
        
        Uses Newton-Raphson iteration to find Eccentric Anomaly (E)
        from Mean Anomaly (M) and eccentricity (e).
        
        Args:
            M: Mean anomaly in radians
            e: Eccentricity (0 <= e < 1 for ellipse)
            tolerance: Convergence tolerance
            max_iter: Maximum iterations
            
        Returns:
            Eccentric anomaly E in radians
        """
        # Initial guess
        if e < 0.8:
            E = M
        else:
            E = math.pi
        
        # Newton-Raphson iteration
        for _ in range(max_iter):
            f = E - e * math.sin(E) - M
            f_prime = 1 - e * math.cos(E)
            E_new = E - f / f_prime
            
            if abs(E_new - E) < tolerance:
                return E_new
            E = E_new
        
        return E  # Return best estimate if not converged
    
    @staticmethod
    def eccentric_to_true_anomaly(E: float, e: float) -> float:
        """
        Convert Eccentric Anomaly to True Anomaly.
        
        Args:
            E: Eccentric anomaly in radians
            e: Eccentricity
            
        Returns:
            True anomaly (nu) in radians
        """
        # Using the half-angle formula
        beta = e / (1 + math.sqrt(1 - e**2))
        nu = E + 2 * math.atan2(beta * math.sin(E), 1 - beta * math.cos(E))
        return nu
    
    @staticmethod
    def orbital_radius(a: float, e: float, nu: float) -> float:
        """
        Calculate orbital radius at given true anomaly.
        
        Args:
            a: Semi-major axis (AU or km)
            e: Eccentricity
            nu: True anomaly in radians
            
        Returns:
            Radius in same units as a
        """
        return a * (1 - e**2) / (1 + e * math.cos(nu))
    
    @staticmethod
    def mean_motion(a_au: float) -> float:
        """
        Calculate mean motion (orbital angular velocity) in radians/day.
        
        Uses Kepler's third law: T² = a³ (with T in years, a in AU)
        
        Args:
            a_au: Semi-major axis in AU
            
        Returns:
            Mean motion in radians per day
        """
        # Period in years from Kepler's third law
        period_years = math.sqrt(a_au ** 3)
        period_days = period_years * 365.25
        
        # Mean motion = 2π / period
        return 2 * math.pi / period_days
    
    @classmethod
    def propagate_mean_anomaly(cls, elements: OrbitalElements, target_time: datetime) -> float:
        """
        Propagate mean anomaly from epoch to target time.
        
        Args:
            elements: Orbital elements with epoch
            target_time: Time to propagate to
            
        Returns:
            Mean anomaly at target time (degrees)
        """
        # Time difference in days
        dt = (target_time - elements.epoch).total_seconds() / 86400.0
        
        # Mean motion
        n = cls.mean_motion(elements.semi_major_axis)
        
        # New mean anomaly (wrapped to 0-360)
        M_new = (elements.mean_anomaly * DEG_TO_RAD + n * dt) % (2 * math.pi)
        
        return M_new * RAD_TO_DEG
    
    @classmethod
    def orbital_elements_to_cartesian(
        cls, 
        elements: OrbitalElements, 
        target_time: Optional[datetime] = None
    ) -> CartesianState:
        """
        Convert orbital elements to Cartesian coordinates.
        
        Returns heliocentric ecliptic coordinates (Sun at origin).
        
        Args:
            elements: Keplerian orbital elements
            target_time: Time for position calculation (defaults to epoch)
            
        Returns:
            CartesianState with position in km
        """
        # Use epoch if no target time specified
        if target_time is None:
            target_time = elements.epoch
        
        # Convert elements to radians
        a = elements.semi_major_axis * AU_TO_KM  # Convert to km
        e = elements.eccentricity
        i = elements.inclination * DEG_TO_RAD
        Omega = elements.longitude_ascending_node * DEG_TO_RAD
        omega = elements.argument_perihelion * DEG_TO_RAD
        
        # Propagate mean anomaly to target time
        M = cls.propagate_mean_anomaly(elements, target_time) * DEG_TO_RAD
        
        # Solve Kepler's equation for eccentric anomaly
        E = cls.solve_kepler_equation(M, e)
        
        # True anomaly
        nu = cls.eccentric_to_true_anomaly(E, e)
        
        # Radius at this position
        r = cls.orbital_radius(a, e, nu)
        
        # Position in orbital plane
        x_orbital = r * math.cos(nu)
        y_orbital = r * math.sin(nu)
        
        # Rotation matrices to ecliptic frame
        # First rotate by argument of perihelion
        cos_omega = math.cos(omega)
        sin_omega = math.sin(omega)
        x1 = cos_omega * x_orbital - sin_omega * y_orbital
        y1 = sin_omega * x_orbital + cos_omega * y_orbital
        z1 = 0.0
        
        # Rotate by inclination
        cos_i = math.cos(i)
        sin_i = math.sin(i)
        x2 = x1
        y2 = cos_i * y1
        z2 = sin_i * y1
        
        # Rotate by longitude of ascending node
        cos_Omega = math.cos(Omega)
        sin_Omega = math.sin(Omega)
        x_ecl = cos_Omega * x2 - sin_Omega * y2
        y_ecl = sin_Omega * x2 + cos_Omega * y2
        z_ecl = z2
        
        return CartesianState(x=x_ecl, y=y_ecl, z=z_ecl)
    
    @classmethod
    def generate_orbit_points(
        cls,
        elements: OrbitalElements,
        num_points: int = 100,
        center_on_earth: bool = True
    ) -> List[Tuple[float, float, float]]:
        """
        Generate points along the asteroid's orbit for visualization.
        
        Args:
            elements: Orbital elements
            num_points: Number of points to generate
            center_on_earth: If True, subtract Earth's position to get geocentric coords
            
        Returns:
            List of (x, y, z) tuples in km
        """
        points = []
        
        # Calculate orbital period
        period_years = math.sqrt(elements.semi_major_axis ** 3)
        period_days = period_years * 365.25
        
        # Generate points for one complete orbit
        for i in range(num_points):
            # Time offset for this point
            t_offset = timedelta(days=(i / num_points) * period_days)
            target_time = elements.epoch + t_offset
            
            # Get position at this time
            state = cls.orbital_elements_to_cartesian(elements, target_time)
            
            if center_on_earth:
                # Approximate Earth position (simplified - circular orbit at 1 AU)
                # For accurate results, you'd calculate Earth's position too
                earth_angle = (i / num_points) * 2 * math.pi
                earth_x = AU_TO_KM * math.cos(earth_angle)
                earth_y = AU_TO_KM * math.sin(earth_angle)
                
                points.append((
                    state.x - earth_x,
                    state.y - earth_y, 
                    state.z
                ))
            else:
                points.append((state.x, state.y, state.z))
        
        return points
    
    @classmethod
    def calculate_close_approach(
        cls,
        elements: OrbitalElements,
        days_ahead: int = 365
    ) -> Tuple[datetime, float]:
        """
        Find the closest approach to Earth within a time window.
        
        Args:
            elements: Asteroid orbital elements
            days_ahead: Number of days to search
            
        Returns:
            Tuple of (closest_approach_time, minimum_distance_km)
        """
        min_distance = float('inf')
        min_time = elements.epoch
        
        # Sample positions (could be optimized with binary search)
        for day in range(days_ahead):
            target_time = elements.epoch + timedelta(days=day)
            
            # Asteroid position
            ast_state = cls.orbital_elements_to_cartesian(elements, target_time)
            
            # Simplified Earth position (circular orbit)
            days_since_epoch = (target_time - datetime(target_time.year, 1, 1)).days
            earth_angle = (days_since_epoch / 365.25) * 2 * math.pi
            earth_x = AU_TO_KM * math.cos(earth_angle)
            earth_y = AU_TO_KM * math.sin(earth_angle)
            
            # Distance
            distance = math.sqrt(
                (ast_state.x - earth_x)**2 + 
                (ast_state.y - earth_y)**2 + 
                ast_state.z**2
            )
            
            if distance < min_distance:
                min_distance = distance
                min_time = target_time
        
        return min_time, min_distance


# Example orbital elements for well-known asteroids
EXAMPLE_ASTEROIDS = {
    "apophis": OrbitalElements(
        name="99942 Apophis",
        semi_major_axis=0.9224,
        eccentricity=0.1911,
        inclination=3.331,
        longitude_ascending_node=204.446,
        argument_perihelion=126.393,
        mean_anomaly=180.0,
        epoch=datetime(2024, 1, 1),
        diameter_m=370,
        is_potentially_hazardous=True
    ),
    "bennu": OrbitalElements(
        name="101955 Bennu",
        semi_major_axis=1.126,
        eccentricity=0.2037,
        inclination=6.035,
        longitude_ascending_node=2.060,
        argument_perihelion=66.223,
        mean_anomaly=101.7,
        epoch=datetime(2024, 1, 1),
        diameter_m=492,
        is_potentially_hazardous=True
    ),
    "eros": OrbitalElements(
        name="433 Eros",
        semi_major_axis=1.458,
        eccentricity=0.2229,
        inclination=10.829,
        longitude_ascending_node=304.3,
        argument_perihelion=178.9,
        mean_anomaly=320.0,
        epoch=datetime(2024, 1, 1),
        diameter_m=16840,
        is_potentially_hazardous=False
    )
}


def get_example_asteroid(name: str) -> Optional[OrbitalElements]:
    """Get example asteroid orbital elements by name."""
    return EXAMPLE_ASTEROIDS.get(name.lower())
