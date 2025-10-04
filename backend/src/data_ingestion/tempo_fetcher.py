"""
Module: tempo_fetcher
Description: Fetches TEMPO satellite data from NASA Earthdata
Author: NASA Space Apps Team
Created: October 4, 2025
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import earthaccess
import requests
import os

logger = logging.getLogger(__name__)
# Define the dataset short name for TEMPO NO2 Level 2 data
TEMPO_NO2_SHORT_NAME = "TEMPO_NO2_L2"
DOWNLOAD_DIR = "tempo_data_downloads"

class TEMPOFetcher:
    """
    TEMPO Satellite Data Fetcher
    
    Fetches air quality data from NASA's TEMPO (Tropospheric Emissions: 
    Monitoring of Pollution) satellite mission.
    
    Attributes:
        api_key (str): NASA Earthdata API key
        base_url (str): Base URL for TEMPO data API
        auth (earthaccess.auth.Auth): earthaccess authentication object.

    """
    
    def __init__(self, api_key: str) -> None:  # api_key is unused in earthaccess, but kept for signature
        """
        Initialize TEMPOFetcher
        
        Args:
            api_key: NASA Earthdata API key (unused when earthaccess is used)
        """
        # self.api_key = api_key
        # self.base_url = "https://earthdata.nasa.gov/tempo"
        self.auth = earthaccess.login()
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def fetch_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        bbox: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Fetch TEMPO satellite data for specified date range and bounding box
        
        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            bbox: Bounding box tuple (min_lon, min_lat, max_lon, max_lat)
            
        Returns:
            Dictionary containing TEMPO satellite data
            
        Raises:
            RequestException: When API request fails
            ValueError: When invalid parameters provided
        """
        try:
            # TODO: Implement actual TEMPO data fetching logic
            logger.info(f"Fetching TEMPO data from {start_date} to {end_date}")
            
            # Validate inputs
            if end_date < start_date:
                raise ValueError("end_date must be after start_date")
            
            # Format dates for earthaccess
            temporal_range = (start_date.strftime('%Y-%m-%d'), 
                              end_date.strftime('%Y-%m-%d'))
            
            logger.info(f"Searching for TEMPO NO2 data ({TEMPO_NO2_SHORT_NAME}) from {temporal_range}...")
      
            # Build request parameters
            params = {
                "short_name": TEMPO_NO2_SHORT_NAME,
                "temporal": temporal_range,
                "cloud_hosted": True # TEMPO data is primarily cloud-hosted
            }
            
            if bbox:
                # earthaccess expects bbox as (min_lon, min_lat, max_lon, max_lat)
                # The input tuple (min_lon, min_lat, max_lon, max_lat) matches this
                params["bounding_box"] = bbox 
                logger.info(f"Applying bounding box filter: {bbox}")            
            # TODO: Make actual API request
            # response = requests.get(self.base_url, params=params, 
            #                        headers={"Authorization": f"Bearer {self.api_key}"})
            # response.raise_for_status()
            # return response.json()
            
            results = earthaccess.search_data(**params)
            
            num_granules = len(results)
            logger.info(f"Found {num_granules} matching granules.")
            
            if num_granules == 0:
                return {"status": "success", "message": "No granules found for the specified criteria."}
            
            # 3. Download the granules using earthaccess.download()
            
            # Ensure the download directory exists
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)

            logger.info(f"Starting download to directory: {DOWNLOAD_DIR}")
            
            # The download function takes the search results object directly
            local_files = earthaccess.download(
                results, 
                local_path=DOWNLOAD_DIR
            )
            
            logger.info("TEMPO data downloaded successfully.")
            return {
                "status": "success", 
                "message": f"Downloaded {len(local_files)} files.",
                "files": local_files
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_data: {e}")
            raise
