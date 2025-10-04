"""
Module: tempo_fetcher
Description: Fetches TEMPO satellite data from NASA Earthdata
Author: NASA Space Apps Team
Created: October 4, 2025
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import earthaccess
import requests # Still imported but unused in the current logic
import os

logger = logging.getLogger(__name__)

# --- NEW / UPDATED CONSTANTS ---
DOWNLOAD_DIR = "tempo_data_downloads"

# Define the dataset short names for TEMPO Level 2 data
# NOTE: These names are based on common conventions.
# VERIFY them against the official NASA Earthdata Catalog (CMR) for TEMPO.
TEMPO_SHORT_NAMES = {
    "NO2": "TEMPO_NO2_L2",
    "CH2O": "TEMPO_HCHO_L2",  # Formaldehyde
    "AI": "TEMPO_AEROSOL_L2", # Aerosol Index
    "O3": "TEMPO_O3_L2",      # Ozone
    # NOTE: TEMPO may not have a dedicated PM product.
    # PM is often derived from Aerosol Optical Depth (AOD) or similar fields.
    # We will use the AI short name as a proxy or simply exclude PM,
    # but the structure allows adding a verified name if one exists.
}

# --- END OF NEW / UPDATED CONSTANTS ---

class TEMPOFetcher:
    """
    TEMPO Satellite Data Fetcher
    
    Fetches air quality data from NASA's TEMPO (Tropospheric Emissions: 
    Monitoring of Pollution) satellite mission.
    
    Attributes:
        auth (earthaccess.auth.Auth): earthaccess authentication object.
    """
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Initialize TEMPOFetcher
        """
        # earthaccess.login() will attempt to use EARTHDATA_USERNAME/PASSWORD 
        # from environment variables or prompt the user.
        self.auth = earthaccess.login()
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def fetch_data(
        self, 
        start_date: datetime, 
        end_date: datetime,
        constituents: Union[str, List[str]] = "NO2", # ADDED PARAMETER
        bbox: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Fetch TEMPO satellite data for specified date range, constituents, and bounding box
        
        Args:
            start_date: Start date for data retrieval
            end_date: End date for data retrieval
            constituents: A single constituent name (e.g., "NO2") or a list of 
                          names (e.g., ["NO2", "O3", "CH2O"]). Valid keys are 
                          "NO2", "CH2O", "AI", "O3". Defaults to "NO2".
            bbox: Bounding box tuple (min_lon, min_lat, max_lon, max_lat)
            
        Returns:
            Dictionary containing download status and file paths
            
        Raises:
            RequestException: When API request fails
            ValueError: When invalid parameters provided or invalid constituent requested
        """
        try:
            # 1. Input Validation
            if end_date < start_date:
                raise ValueError("end_date must be after start_date")
            
            if isinstance(constituents, str):
                constituents = [constituents]
                
            # Convert constituent names to Earthdata Short Names
            short_names = []
            for c in constituents:
                short_name = TEMPO_SHORT_NAMES.get(c.upper())
                if short_name is None:
                    raise ValueError(
                        f"Invalid constituent '{c}'. Valid options: {list(TEMPO_SHORT_NAMES.keys())}"
                    )
                short_names.append(short_name)

            if not short_names:
                 raise ValueError("No valid short names derived from constituents list.")
                
            # Log the request
            constituents_str = ", ".join(constituents)
            logger.info(f"Fetching TEMPO data for {constituents_str} from {start_date} to {end_date}")
            
            # 2. Prepare earthaccess query
            temporal_range = (start_date.strftime('%Y-%m-%d'), 
                              end_date.strftime('%Y-%m-%d'))
            
            logger.info(f"Searching for data ({short_names}) from {temporal_range}...")
        
            # Build request parameters for earthaccess
            # earthaccess.search_data can take a list of short names
            params = {
                "short_name": short_names,
                "temporal": temporal_range,
                "cloud_hosted": True # TEMPO data is primarily cloud-hosted
            }
            
            if bbox:
                params["bounding_box"] = bbox 
                logger.info(f"Applying bounding box filter: {bbox}") 
                
            # 3. Search for data
            results = earthaccess.search_data(**params)
            
            num_granules = len(results)
            logger.info(f"Found {num_granules} matching granules.")
            
            if num_granules == 0:
                return {"status": "success", "message": "No granules found for the specified criteria."}
            
            # 4. Download the granules
            
            # Ensure the download directory exists
            if not os.path.exists(DOWNLOAD_DIR):
                os.makedirs(DOWNLOAD_DIR)

            logger.info(f"Starting download of {num_granules} granules to: {DOWNLOAD_DIR}")
            
            # The download function takes the search results object directly
            local_files = earthaccess.download(
                results, 
                local_path=DOWNLOAD_DIR
            )
            
            logger.info(f"TEMPO data downloaded successfully. Files: {len(local_files)}")
            return {
                "status": "success", 
                "message": f"Downloaded {len(local_files)} files.",
                "files": local_files
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_data: {e}")
            raise

# --- EXAMPLE USAGE (for demonstration, not part of the class) ---
if __name__ == '__main__':
    # Set up basic logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Example of how you would use it:
    try:
        # NOTE: You MUST have your EARTHDATA_USERNAME and EARTHDATA_PASSWORD 
        # set in your environment variables for earthaccess.login() to work
        # without prompting you.
        fetcher = TEMPOFetcher()
        
        start_date = datetime(2025, 10, 1)
        end_date = datetime(2025, 10, 4)
        
        # Bounding box for New York City area (approx)
        nyc_bbox = (-75.0, 40.0, -73.0, 41.0) 
        
        # Fetch NO2, Ozone, and Formaldehyde data
        results = fetcher.fetch_data(
            start_date=start_date,
            end_date=end_date,
            constituents=["NO2", "O3", "CH2O"],
            bbox=nyc_bbox
        )
        
        print("\n--- Download Results ---")
        print(f"Status: {results['status']}")
        print(f"Message: {results['message']}")
        # print(f"Files: {results.get('files', 'No files downloaded')}")

    except Exception as e:
        print(f"\nAn error occurred during execution: {e}")