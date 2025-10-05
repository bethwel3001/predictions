"""
Module: openaq_fetcher
Description: Fetches global air quality data from OpenAQ platform
Author: NASA Space Apps Team
Created: October 4, 2025
Updated: October 5, 2025 - Migrated to OpenAQ API v3

OpenAQ provides open air quality data from thousands of ground-based monitoring stations globally.
API Documentation: https://docs.openaq.org/
API v3 Documentation: https://docs.openaq.org/docs/introduction
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests

logger = logging.getLogger(__name__)


class OpenAQFetcher:
    """
    OpenAQ Air Quality Data Fetcher (API v3)
    
    Fetches real-time and historical air quality data from OpenAQ platform.
    OpenAQ aggregates air quality data from government monitoring stations,
    research institutions, and other sources worldwide.
    
    Attributes:
        base_url (str): Base URL for OpenAQ API v3
        api_key (Optional[str]): API key for enhanced rate limits (optional)
    """
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Initialize OpenAQFetcher with API v3
        
        Args:
            api_key: Optional API key for higher rate limits
        """
        self.base_url = "https://api.openaq.org/v3"
        self.api_key = api_key
        self.headers = {
            "Accept": "application/json"
        }
        
        if api_key:
            self.headers["X-API-Key"] = api_key
            
        logger.info(f"Initialized {self.__class__.__name__} with API v3")
    
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
        Fetch latest air quality measurements from OpenAQ API v3
        
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
            # API v3 uses /locations endpoint for latest measurements
            endpoint = f"{self.base_url}/locations"
            
            params: Dict[str, Any] = {"limit": limit}
            
            # v3 API parameter mapping
            if country:
                params["countries"] = country  # v3 uses 'countries' instead of 'country'
            if city:
                params["city"] = city
            if coordinates:
                # v3 uses separate lat/lon parameters or coordinates parameter
                params["coordinates"] = f"{coordinates[0]},{coordinates[1]}"
                params["radius"] = radius
            if parameter:
                params["parameters"] = parameter  # v3 uses 'parameters' instead of 'parameter'
                
            logger.info(f"Fetching OpenAQ v3 latest measurements with params: {params}")
            
            response = requests.get(
                endpoint,
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"Successfully fetched {len(data.get('results', []))} measurements from OpenAQ v3")
            
            # Add data attribution metadata
            data['_attribution'] = {
                'source': 'OpenAQ API v3',
                'url': 'https://openaq.org',
                'license': 'CC BY 4.0',
                'api_version': 'v3',
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching OpenAQ v3 data: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
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
        Fetch available monitoring locations from OpenAQ API v3
        
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
            
            params: Dict[str, Any] = {"limit": limit}
            
            # v3 API parameter adjustments
            if country:
                params["countries"] = country  # v3 uses 'countries'
            if city:
                params["city"] = city
            if coordinates:
                params["coordinates"] = f"{coordinates[0]},{coordinates[1]}"
                params["radius"] = radius
                
            logger.info(f"Fetching OpenAQ v3 locations")
            
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
                'source': 'OpenAQ API v3',
                'url': 'https://openaq.org',
                'license': 'CC BY 4.0',
                'api_version': 'v3',
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
        Fetch historical measurements for a specific location (API v3)
        
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
            # v3 API uses different endpoint structure
            endpoint = f"{self.base_url}/locations/{location_id}/measurements"
            
            params: Dict[str, Any] = {
                "limit": limit
            }
            
            if parameter:
                params["parameters"] = parameter  # v3 uses 'parameters'
            if date_from:
                params["date_from"] = date_from.isoformat()
            if date_to:
                params["date_to"] = date_to.isoformat()
                
            logger.info(f"Fetching measurements for location {location_id} from API v3")
            
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
                'source': 'OpenAQ API v3',
                'url': 'https://openaq.org',
                'license': 'CC BY 4.0',
                'api_version': 'v3',
                'fetched_at': datetime.utcnow().isoformat()
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error in fetch_measurements_by_location: {e}")
            raise
    
    def get_available_parameters(self) -> List[Dict[str, Any]]:
        """
        Get list of available pollutant parameters from OpenAQ API v3
        
        Returns:
            List of parameter dictionaries
        """
        try:
            endpoint = f"{self.base_url}/parameters"
            
            logger.info("Fetching available parameters from OpenAQ API v3")
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            
            # v3 API structure - may need to adapt based on actual response
            results = data.get('results', [])
            logger.info(f"Found {len(results)} available parameters")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in get_available_parameters: {e}")
            logger.error(f"Response: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
            raise
