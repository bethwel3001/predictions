"""
Module: openaq_fetcher
Description: Fetches global air quality data from OpenAQ platform
Author: NASA Space Apps Team
Created: October 4, 2025

OpenAQ provides open air quality data from thousands of ground-based monitoring stations globally.
API Documentation: https://docs.openaq.org/
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class OpenAQFetcher:
    """
    OpenAQ Air Quality Data Fetcher
    
    Fetches real-time and historical air quality data from OpenAQ platform.
    OpenAQ aggregates air quality data from government monitoring stations,
    research institutions, and other sources worldwide.
    
    Attributes:
        base_url (str): Base URL for OpenAQ API
        api_key (Optional[str]): API key for enhanced rate limits (optional)
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize OpenAQFetcher
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.base_url = "https://api.openaq.org/v2"
        self.api_key = api_key
        self.headers = {}
        
        if api_key:
            self.headers["X-API-Key"] = api_key
            
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def fetch_latest_measurements(
        self,
        country: Optional[str] = None,
        city: Optional[str] = None,
        coordinates: Optional[tuple] = None,
        radius: int = 25000,
        parameter: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch latest air quality measurements from OpenAQ
        
        Args:
            country: Two-letter country code (e.g., 'US', 'CA')
            city: City name
            coordinates: Tuple of (latitude, longitude) for location-based search
            radius: Search radius in meters (default: 25km)
            parameter: Specific pollutant (pm25, pm10, o3, no2, so2, co)
            limit: Maximum number of results (default: 100)
            
        Returns:
            Dictionary containing air quality measurements with metadata
            
        Example:
            >>> fetcher = OpenAQFetcher()
            >>> data = fetcher.fetch_latest_measurements(
            ...     coordinates=(34.05, -118.24),
            ...     parameter='pm25',
            ...     radius=10000
            ... )
        """
        try:
            endpoint = f"{self.base_url}/latest"
            
            params = {"limit": limit}
            
            if country:
                params["country"] = country
            if city:
                params["city"] = city
            if coordinates:
                params["coordinates"] = f"{coordinates[0]},{coordinates[1]}"
                params["radius"] = radius
            if parameter:
                params["parameter"] = parameter
                
            logger.info(f"Fetching OpenAQ latest measurements with params: {params}")
            
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Successfully fetched {len(data.get('results', []))} measurements from OpenAQ")
            
            # Add data attribution metadata
            data['_attribution'] = {
                'source': 'OpenAQ',
                'url': 'https://openaq.org',
                'license': 'CC BY 4.0',
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching OpenAQ data: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in fetch_latest_measurements: {e}")
            raise
    
    def fetch_locations(
        self,
        country: Optional[str] = None,
        city: Optional[str] = None,
        coordinates: Optional[tuple] = None,
        radius: int = 25000,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch available monitoring locations from OpenAQ
        
        Args:
            country: Two-letter country code
            city: City name
            coordinates: Tuple of (latitude, longitude)
            radius: Search radius in meters
            limit: Maximum number of results
            
        Returns:
            Dictionary containing location information
        """
        try:
            endpoint = f"{self.base_url}/locations"
            
            params = {"limit": limit}
            
            if country:
                params["country"] = country
            if city:
                params["city"] = city
            if coordinates:
                params["coordinates"] = f"{coordinates[0]},{coordinates[1]}"
                params["radius"] = radius
                
            logger.info(f"Fetching OpenAQ locations")
            
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Found {len(data.get('results', []))} locations")
            
            # Add data attribution
            data['_attribution'] = {
                'source': 'OpenAQ',
                'url': 'https://openaq.org',
                'license': 'CC BY 4.0',
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in fetch_locations: {e}")
            raise
    
    def fetch_measurements_by_location(
        self,
        location_id: int,
        parameter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Fetch historical measurements for a specific location
        
        Args:
            location_id: OpenAQ location ID
            parameter: Specific pollutant parameter
            date_from: Start date for historical data
            date_to: End date for historical data
            limit: Maximum number of results
            
        Returns:
            Dictionary containing historical measurements
        """
        try:
            endpoint = f"{self.base_url}/measurements"
            
            params = {
                "location_id": location_id,
                "limit": limit
            }
            
            if parameter:
                params["parameter"] = parameter
            if date_from:
                params["date_from"] = date_from.isoformat()
            if date_to:
                params["date_to"] = date_to.isoformat()
                
            logger.info(f"Fetching measurements for location {location_id}")
            
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Fetched {len(data.get('results', []))} measurements")
            
            # Add attribution
            data['_attribution'] = {
                'source': 'OpenAQ',
                'url': 'https://openaq.org',
                'license': 'CC BY 4.0',
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in fetch_measurements_by_location: {e}")
            raise
    
    def get_available_parameters(self) -> List[str]:
        """
        Get list of available pollutant parameters
        
        Returns:
            List of parameter codes (e.g., ['pm25', 'pm10', 'o3', 'no2'])
        """
        try:
            endpoint = f"{self.base_url}/parameters"
            
            response = requests.get(endpoint, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            parameters = [p['name'] for p in data.get('results', [])]
            
            logger.info(f"Available parameters: {parameters}")
            return parameters
            
        except Exception as e:
            logger.error(f"Error getting parameters: {e}")
            raise
