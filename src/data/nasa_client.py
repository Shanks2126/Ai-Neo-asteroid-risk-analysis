"""
NASA Near-Earth Object (NEO) API Client.
Fetches real asteroid data from NASA's public API.
"""

import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json

from src.utils.config import settings
from src.utils.logging import logger


class NASAClient:
    """
    Client for NASA's Near-Earth Object Web Service (NeoWs).
    
    API Documentation: https://api.nasa.gov/
    
    Rate Limits:
        - DEMO_KEY: 30 requests/hour, 50 requests/day
        - Registered key: 1000 requests/hour
    """
    
    BASE_URL = "https://api.nasa.gov/neo/rest/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NASA client.
        
        Args:
            api_key: NASA API key (defaults to settings)
        """
        self.api_key = api_key or settings.nasa_api_key
        self.client = httpx.Client(timeout=30.0)
    
    async def _async_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make async request to NASA API."""
        params = params or {}
        params["api_key"] = self.api_key
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{self.BASE_URL}{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
    
    def _sync_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict:
        """Make sync request to NASA API."""
        params = params or {}
        params["api_key"] = self.api_key
        
        response = self.client.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_feed(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get NEO feed for a date range.
        
        Args:
            start_date: Start date (defaults to today)
            end_date: End date (defaults to 7 days from start)
            
        Returns:
            Dict containing near-Earth objects grouped by date
        """
        start = start_date or datetime.now()
        end = end_date or (start + timedelta(days=7))
        
        params = {
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": end.strftime("%Y-%m-%d")
        }
        
        logger.info(f"Fetching NEO feed from {params['start_date']} to {params['end_date']}")
        return self._sync_request("/feed", params)
    
    def get_neo_by_id(self, neo_id: str) -> Dict:
        """
        Get details for a specific NEO by its ID.
        
        Args:
            neo_id: NEO reference ID
            
        Returns:
            Dict containing asteroid details
        """
        logger.info(f"Fetching NEO details for ID: {neo_id}")
        return self._sync_request(f"/neo/{neo_id}")
    
    def get_neo_browse(self, page: int = 0, size: int = 20) -> Dict:
        """
        Browse the overall asteroid dataset.
        
        Args:
            page: Page number (0-indexed)
            size: Number of items per page
            
        Returns:
            Dict containing paginated asteroid data
        """
        params = {"page": page, "size": size}
        return self._sync_request("/neo/browse", params)
    
    def parse_neo_data(self, neo: Dict) -> Dict[str, Any]:
        """
        Parse raw NEO data into our format.
        
        Args:
            neo: Raw NEO data from NASA API
            
        Returns:
            Parsed data with our feature names
        """
        # Get diameter estimates (prefer kilometers, convert to meters)
        diameter = neo.get("estimated_diameter", {}).get("meters", {})
        diameter_min = diameter.get("estimated_diameter_min", 0)
        diameter_max = diameter.get("estimated_diameter_max", 0)
        diameter_avg = (diameter_min + diameter_max) / 2
        
        # Get close approach data (most recent)
        close_approaches = neo.get("close_approach_data", [])
        
        if close_approaches:
            approach = close_approaches[0]  # Get first/closest approach
            miss_distance = float(approach.get("miss_distance", {}).get("kilometers", 0))
            velocity = float(approach.get("relative_velocity", {}).get("kilometers_per_second", 0))
            approach_date = approach.get("close_approach_date_full", "")
        else:
            miss_distance = 0
            velocity = 0
            approach_date = ""
        
        return {
            "neo_reference_id": neo.get("neo_reference_id"),
            "name": neo.get("name", "Unknown"),
            "distance_km": miss_distance,
            "velocity_kms": velocity,
            "diameter_m": diameter_avg,
            "diameter_min_m": diameter_min,
            "diameter_max_m": diameter_max,
            "trajectory_angle_deg": 45.0,  # NASA doesn't provide this, use default
            "is_potentially_hazardous": neo.get("is_potentially_hazardous_asteroid", False),
            "is_sentry_object": neo.get("is_sentry_object", False),
            "close_approach_date": approach_date,
            "raw_data": json.dumps(neo)
        }
    
    def get_close_approaches_today(self) -> List[Dict[str, Any]]:
        """
        Get all NEOs with close approaches today.
        
        Returns:
            List of parsed NEO data
        """
        today = datetime.now()
        feed = self.get_feed(today, today)
        
        neos = []
        for date_str, neo_list in feed.get("near_earth_objects", {}).items():
            for neo in neo_list:
                parsed = self.parse_neo_data(neo)
                neos.append(parsed)
        
        logger.info(f"Found {len(neos)} NEOs with close approaches today")
        return neos
    
    def get_hazardous_asteroids(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get potentially hazardous asteroids for the next N days.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of hazardous NEOs
        """
        start = datetime.now()
        end = start + timedelta(days=days)
        feed = self.get_feed(start, end)
        
        hazardous = []
        for date_str, neo_list in feed.get("near_earth_objects", {}).items():
            for neo in neo_list:
                if neo.get("is_potentially_hazardous_asteroid", False):
                    parsed = self.parse_neo_data(neo)
                    hazardous.append(parsed)
        
        logger.info(f"Found {len(hazardous)} hazardous NEOs in next {days} days")
        return hazardous


# Singleton instance
nasa_client = NASAClient()
