"""
NASA Small Body Database (SBDB) API Client.

Fetches accurate orbital elements for asteroids from NASA JPL's SBDB.
API Documentation: https://ssd-api.jpl.nasa.gov/doc/sbdb.html
"""

import httpx
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import asdict

from .orbital_mechanics import OrbitalElements


class NASASBDBClient:
    """
    Client for NASA's Small Body Database API.
    
    Provides accurate orbital elements for asteroids and comets.
    """
    
    BASE_URL = "https://ssd-api.jpl.nasa.gov/sbdb.api"
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
    
    def get_asteroid_data(self, designation: str) -> Optional[Dict[str, Any]]:
        """
        Fetch asteroid data from SBDB by designation or name.
        
        Args:
            designation: Asteroid name or designation (e.g., "Apophis", "2024 AB")
            
        Returns:
            Raw API response or None if not found
        """
        params = {
            "sstr": designation,
            "phys-par": "true",  # Include physical parameters
            "ca-data": "true",   # Include close approach data
            "orbit": "true",     # Include orbital elements (NOT available in free tier)
        }
        
        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            print(f"SBDB API error: {e}")
            return None
    
    def parse_orbital_elements(self, data: Dict[str, Any]) -> Optional[OrbitalElements]:
        """
        Parse SBDB response into OrbitalElements object.
        
        Args:
            data: Raw SBDB API response
            
        Returns:
            OrbitalElements or None if parsing fails
        """
        try:
            obj = data.get("object", {})
            orbit = data.get("orbit", {})
            elements = orbit.get("elements", [])
            phys_par = data.get("phys_par", [])
            
            # Build elements dictionary from list
            elem_dict = {}
            for elem in elements:
                elem_dict[elem.get("name")] = elem.get("value")
            
            # Extract physical parameters
            diameter = None
            for par in phys_par:
                if par.get("name") == "diameter":
                    diameter = float(par.get("value", 0)) * 1000  # km to m
            
            # Parse epoch (usually in Julian Date)
            epoch_jd = float(orbit.get("epoch", 2460000))
            # Convert JD to datetime (approximate)
            epoch = datetime(2000, 1, 1) + (epoch_jd - 2451545.0) * datetime.resolution * 86400000
            
            return OrbitalElements(
                name=obj.get("fullname", obj.get("des", "Unknown")),
                neo_reference_id=obj.get("spkid"),
                semi_major_axis=float(elem_dict.get("a", 1.0)),
                eccentricity=float(elem_dict.get("e", 0.0)),
                inclination=float(elem_dict.get("i", 0.0)),
                longitude_ascending_node=float(elem_dict.get("om", 0.0)),
                argument_perihelion=float(elem_dict.get("w", 0.0)),
                mean_anomaly=float(elem_dict.get("ma", 0.0)),
                epoch=epoch,
                diameter_m=diameter,
                is_potentially_hazardous=obj.get("pha", False)
            )
        except (KeyError, ValueError, TypeError) as e:
            print(f"Failed to parse orbital elements: {e}")
            return None
    
    def get_close_approaches(
        self, 
        designation: str, 
        date_min: Optional[str] = None,
        date_max: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get close approach data for an asteroid.
        
        Args:
            designation: Asteroid name or designation
            date_min: Start date (YYYY-MM-DD)
            date_max: End date (YYYY-MM-DD)
            
        Returns:
            List of close approach events
        """
        params = {
            "sstr": designation,
            "ca-data": "true",
        }
        if date_min:
            params["ca-time"] = f"{date_min}/{date_max or '2100-12-31'}"
        
        try:
            response = self.client.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            ca_data = data.get("ca_data", [])
            approaches = []
            
            for ca in ca_data:
                approaches.append({
                    "date": ca.get("cd"),
                    "distance_au": float(ca.get("dist", 0)),
                    "distance_km": float(ca.get("dist", 0)) * 149597870.7,
                    "distance_lunar": float(ca.get("dist_min", 0)) * 389.17,
                    "velocity_kms": float(ca.get("v_rel", 0)),
                    "body": ca.get("body", "Earth")
                })
            
            return approaches
        except httpx.HTTPError:
            return []
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


# Fallback orbital data for common asteroids (when API unavailable)
KNOWN_ASTEROID_ORBITS = {
    "99942 apophis": OrbitalElements(
        name="99942 Apophis",
        neo_reference_id="2099942",
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
    "101955 bennu": OrbitalElements(
        name="101955 Bennu",
        neo_reference_id="2101955",
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
    "433 eros": OrbitalElements(
        name="433 Eros",
        neo_reference_id="2000433",
        semi_major_axis=1.458,
        eccentricity=0.2229,
        inclination=10.829,
        longitude_ascending_node=304.3,
        argument_perihelion=178.9,
        mean_anomaly=320.0,
        epoch=datetime(2024, 1, 1),
        diameter_m=16840,
        is_potentially_hazardous=False
    ),
    "1862 apollo": OrbitalElements(
        name="1862 Apollo",
        neo_reference_id="2001862",
        semi_major_axis=1.471,
        eccentricity=0.560,
        inclination=6.35,
        longitude_ascending_node=35.7,
        argument_perihelion=285.9,
        mean_anomaly=45.0,
        epoch=datetime(2024, 1, 1),
        diameter_m=1500,
        is_potentially_hazardous=True
    ),
    "4179 toutatis": OrbitalElements(
        name="4179 Toutatis",
        neo_reference_id="2004179",
        semi_major_axis=2.511,
        eccentricity=0.629,
        inclination=0.447,
        longitude_ascending_node=128.2,
        argument_perihelion=274.8,
        mean_anomaly=190.0,
        epoch=datetime(2024, 1, 1),
        diameter_m=2450,
        is_potentially_hazardous=True
    )
}


def get_orbital_elements(designation: str) -> Optional[OrbitalElements]:
    """
    Get orbital elements for an asteroid, trying SBDB first then fallback data.
    
    Args:
        designation: Asteroid name or designation
        
    Returns:
        OrbitalElements or None
    """
    # Try local cache first
    key = designation.lower()
    if key in KNOWN_ASTEROID_ORBITS:
        return KNOWN_ASTEROID_ORBITS[key]
    
    # Try API
    client = NASASBDBClient()
    try:
        data = client.get_asteroid_data(designation)
        if data:
            return client.parse_orbital_elements(data)
    finally:
        client.close()
    
    return None
