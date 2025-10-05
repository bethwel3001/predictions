"""
Module: pandora_fetcher
Description: Fetches atmospheric column measurements from NASA's Pandora Project
Author: NASA Space Apps Team
Created: October 5, 2025 (Modified for E-A-A focus and earthaccess integration)

NASA's Pandora Project provides ground-based column measurements of trace gases
using the Pandonia Global Network (PGN). Data is accessed via the NASA Earthdata system.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import os # Import the os module to check environment variables

# Import the necessary NASA Earthdata access library
try:
    import earthaccess
    # Define a custom EarthdataLoginError for cleaner error handling later
    from earthaccess.errors import EarthdataLoginError 
except ImportError:
    raise ImportError("The 'earthaccess' library is required. Please install it with 'pip install earthaccess'.")

logger = logging.getLogger(__name__)


# PGN data is often associated with a specific NASA DAAC collection short name.
# This is a key identifier for earthaccess to find the data.
PGN_COLLECTION_SHORTNAME = "Pandora_Level2_TotalColumn_NO2" # Example short name
EXAMPLE_INSTRUMENT_ID = "Pandora135s1" # Example ID for Athens-NOA

class PandoraFetcher:
    """
    NASA Pandora Project Data Fetcher using earthaccess.
    
    Fetches ground-based column measurements of atmospheric trace gases
    from the Pandora network via NASA Earthdata.
    """
    
    def __init__(self) -> None:
        """Initialize PandoraFetcher and authenticate with Earthdata Login."""
        
        self.data_products = {
            'NO2': 'Nitrogen Dioxide column',
            'O3': 'Ozone column',
            'HCHO': 'Formaldehyde column',
            # ... (Other products remain the same)
        }
        self.target_continents = ['Europe', 'Africa', 'Asia']
        
        logger.info(f"Initialized {self.__class__.__name__}. Attempting Earthdata authentication...")
        
        # --- MODIFICATION START ---
        
        # 1. Check for the required environment variables
        username_set = "EARTHDATA_USERNAME" in os.environ
        password_set = "EARTHDATA_PASSWORD" in os.environ
        
        if not (username_set and password_set):
            error_msg = ("EARTHDATA_USERNAME and EARTHDATA_PASSWORD environment variables MUST be set "
                         "for non-interactive authentication.")
            logger.error(error_msg)
            # Raise an error early if environment is misconfigured
            raise EnvironmentError(error_msg)

        try:
            # 2. Authenticate explicitly using the 'environment' strategy.
            # earthaccess will automatically pull the values from os.environ.
            auth = earthaccess.login(strategy="environment")
            
            if not auth.authenticated:
                 # This check catches issues where the credentials were found but were invalid
                raise EarthdataLoginError("Authentication failed: Credentials found in environment are invalid.")
                
            logger.info("Earthaccess authentication successful using environment variables.")
            
        except EarthdataLoginError as e:
            logger.error(f"Earthaccess authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Earthaccess login: {e}")
            raise

        # --- MODIFICATION END ---


    # --- CORE FETCH METHOD (No changes needed here, as 'auth' is handled by the __init__) ---
    def fetch_site_data(
        self,
        site_id: str,
        product: str = 'NO2',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        instrument_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch actual Pandora data using earthaccess by searching the NASA CMR.
        
        Args:
            site_id: The short site identifier (e.g., 'athens').
            product: The data product (e.g., 'NO2').
            start_date: Start time for data retrieval.
            end_date: End time for data retrieval.
            instrument_id: Specific Pandora instrument ID (required for precision).
            
        Returns:
            Dictionary containing metadata and the list of downloaded files.
        """
        
        if product.upper() != 'NO2':
            # This is a simplification; different products may require different collection short names.
            raise NotImplementedError("Earthaccess fetch is only implemented for 'NO2' in this example.")
            
        if instrument_id is None:
            # In a real system, you'd map site_id to an Instrument ID list.
            instrument_id = EXAMPLE_INSTRUMENT_ID
            logger.warning(f"Using default Instrument ID: {instrument_id}. This is crucial for filtering.")
            
        if start_date is None:
            # Default to a recent 24-hour window for testing
            end_date = end_date or datetime.utcnow()
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time_str = start_date.isoformat()
            end_time_str = end_date.isoformat()
        else:
            start_time_str = start_date.isoformat()
            end_time_str = end_date.isoformat() if end_date else datetime.utcnow().isoformat()
        
        logger.info(f"Searching NASA CMR for PGN data (Collection: {PGN_COLLECTION_SHORTNAME})...")
        
        try:
            # 1. Search for granules matching the criteria
            search_results = earthaccess.search_data(
                short_name=PGN_COLLECTION_SHORTNAME,
                temporal=(start_time_str, end_time_str),
                instrument=instrument_id,
            )
            
            num_granules = len(search_results)
            logger.info(f"Found {num_granules} data granule(s) matching the criteria.")
            
            if num_granules == 0:
                return {
                    'site_id': site_id,
                    'product': product,
                    'status': 'SUCCESS_NO_DATA_FOUND',
                    'message': f"No data granules found for {instrument_id} in time range.",
                }
            
            # 2. Download the granules
            downloaded_files = earthaccess.download(search_results)
            
            return {
                'site_id': site_id,
                'product': product,
                'status': 'SUCCESS_EARTHACCESS_FETCH',
                'files_downloaded': downloaded_files,
                'files_count': len(downloaded_files),
                'message': f"Successfully downloaded {len(downloaded_files)} files.",
                '_attribution': {
                    'source': 'NASA Pandonia Global Network (via Earthaccess)',
                    'collection': PGN_COLLECTION_SHORTNAME,
                    'instrument': instrument_id,
                    'time_range': f"{start_time_str} to {end_time_str}",
                    'fetched_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            # The authentication exception is now handled in __init__, but this
            # catches general search/download failures.
            logger.error(f"An error occurred during search or download: {e}")
            return {'status': 'FAILURE_UNKNOWN', 'error': str(e)}

    # --- Other Methods (fetch_site_list, _generate_mock_column_data, etc., remain the same) ---
    def fetch_site_list(self, continent: Optional[str] = None) -> Dict[str, Any]:
        # ... (Existing mock implementation remains the same) ...
        # PGN Sites focused on Europe, Africa, and Asia with coordinates
        all_sites = [
            {'site_id': 'athens', 'name': 'Athens, Greece', 'coordinates': (37.975, 23.789),
             'country': 'GR', 'continent': 'Europe', 'active': True},
            {'site_id': 'seoul', 'name': 'Seoul, South Korea', 'coordinates': (37.58, 127.05),
             'country': 'KR', 'continent': 'Asia', 'active': True},
            # ... (other sites)
        ]
        
        if continent:
            sites_filtered = [s for s in all_sites if s['continent'].lower() == continent.lower()]
        else:
            sites_filtered = all_sites
            
        return {'results': sites_filtered, '_attribution': {'source': 'NASA Pandora Project (Mock List)'}}
        """
Module: pandora_fetcher
Description: Fetches atmospheric column measurements from NASA's Pandora Project
Author: NASA Space Apps Team
Created: October 5, 2025 (Modified for E-A-A focus and earthaccess integration)

NASA's Pandora Project provides ground-based column measurements of trace gases
using the Pandonia Global Network (PGN). Data is accessed via the NASA Earthdata system.
"""

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import os # Import the os module to check environment variables

# Import the necessary NASA Earthdata access library
try:
    import earthaccess
    # Define a custom EarthdataLoginError for cleaner error handling later
    from earthaccess.errors import EarthdataLoginError 
except ImportError:
    raise ImportError("The 'earthaccess' library is required. Please install it with 'pip install earthaccess'.")

logger = logging.getLogger(__name__)


# PGN data is often associated with a specific NASA DAAC collection short name.
# This is a key identifier for earthaccess to find the data.
PGN_COLLECTION_SHORTNAME = "Pandora_Level2_TotalColumn_NO2" # Example short name
EXAMPLE_INSTRUMENT_ID = "Pandora135s1" # Example ID for Athens-NOA

class PandoraFetcher:
    """
    NASA Pandora Project Data Fetcher using earthaccess.
    
    Fetches ground-based column measurements of atmospheric trace gases
    from the Pandora network via NASA Earthdata.
    """
    
    def __init__(self) -> None:
        """Initialize PandoraFetcher and authenticate with Earthdata Login."""
        
        self.data_products = {
            'NO2': 'Nitrogen Dioxide column',
            'O3': 'Ozone column',
            'HCHO': 'Formaldehyde column',
            # ... (Other products remain the same)
        }
        self.target_continents = ['Europe', 'Africa', 'Asia']
        
        logger.info(f"Initialized {self.__class__.__name__}. Attempting Earthdata authentication...")
        
        # --- MODIFICATION START ---
        
        # 1. Check for the required environment variables
        username_set = "EARTHDATA_USERNAME" in os.environ
        password_set = "EARTHDATA_PASSWORD" in os.environ
        
        if not (username_set and password_set):
            error_msg = ("EARTHDATA_USERNAME and EARTHDATA_PASSWORD environment variables MUST be set "
                         "for non-interactive authentication.")
            logger.error(error_msg)
            # Raise an error early if environment is misconfigured
            raise EnvironmentError(error_msg)

        try:
            # 2. Authenticate explicitly using the 'environment' strategy.
            # earthaccess will automatically pull the values from os.environ.
            auth = earthaccess.login(strategy="environment")
            
            if not auth.authenticated:
                 # This check catches issues where the credentials were found but were invalid
                raise EarthdataLoginError("Authentication failed: Credentials found in environment are invalid.")
                
            logger.info("Earthaccess authentication successful using environment variables.")
            
        except EarthdataLoginError as e:
            logger.error(f"Earthaccess authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Earthaccess login: {e}")
            raise

        # --- MODIFICATION END ---


    # --- CORE FETCH METHOD (No changes needed here, as 'auth' is handled by the __init__) ---
    def fetch_site_data(
        self,
        site_id: str,
        product: str = 'NO2',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        instrument_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch actual Pandora data using earthaccess by searching the NASA CMR.
        
        Args:
            site_id: The short site identifier (e.g., 'athens').
            product: The data product (e.g., 'NO2').
            start_date: Start time for data retrieval.
            end_date: End time for data retrieval.
            instrument_id: Specific Pandora instrument ID (required for precision).
            
        Returns:
            Dictionary containing metadata and the list of downloaded files.
        """
        
        if product.upper() != 'NO2':
            # This is a simplification; different products may require different collection short names.
            raise NotImplementedError("Earthaccess fetch is only implemented for 'NO2' in this example.")
            
        if instrument_id is None:
            # In a real system, you'd map site_id to an Instrument ID list.
            instrument_id = EXAMPLE_INSTRUMENT_ID
            logger.warning(f"Using default Instrument ID: {instrument_id}. This is crucial for filtering.")
            
        if start_date is None:
            # Default to a recent 24-hour window for testing
            end_date = end_date or datetime.utcnow()
            start_date = end_date.replace(hour=0, minute=0, second=0, microsecond=0)
            start_time_str = start_date.isoformat()
            end_time_str = end_date.isoformat()
        else:
            start_time_str = start_date.isoformat()
            end_time_str = end_date.isoformat() if end_date else datetime.utcnow().isoformat()
        
        logger.info(f"Searching NASA CMR for PGN data (Collection: {PGN_COLLECTION_SHORTNAME})...")
        
        try:
            # 1. Search for granules matching the criteria
            search_results = earthaccess.search_data(
                short_name=PGN_COLLECTION_SHORTNAME,
                temporal=(start_time_str, end_time_str),
                instrument=instrument_id,
            )
            
            num_granules = len(search_results)
            logger.info(f"Found {num_granules} data granule(s) matching the criteria.")
            
            if num_granules == 0:
                return {
                    'site_id': site_id,
                    'product': product,
                    'status': 'SUCCESS_NO_DATA_FOUND',
                    'message': f"No data granules found for {instrument_id} in time range.",
                }
            
            # 2. Download the granules
            downloaded_files = earthaccess.download(search_results)
            
            return {
                'site_id': site_id,
                'product': product,
                'status': 'SUCCESS_EARTHACCESS_FETCH',
                'files_downloaded': downloaded_files,
                'files_count': len(downloaded_files),
                'message': f"Successfully downloaded {len(downloaded_files)} files.",
                '_attribution': {
                    'source': 'NASA Pandonia Global Network (via Earthaccess)',
                    'collection': PGN_COLLECTION_SHORTNAME,
                    'instrument': instrument_id,
                    'time_range': f"{start_time_str} to {end_time_str}",
                    'fetched_at': datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            # The authentication exception is now handled in __init__, but this
            # catches general search/download failures.
            logger.error(f"An error occurred during search or download: {e}")
            return {'status': 'FAILURE_UNKNOWN', 'error': str(e)}

    # --- Other Methods (fetch_site_list, _generate_mock_column_data, etc., remain the same) ---
    def fetch_site_list(self, continent: Optional[str] = None) -> Dict[str, Any]:
        # ... (Existing mock implementation remains the same) ...
        # PGN Sites focused on Europe, Africa, and Asia with coordinates
        all_sites = [
            {'site_id': 'athens', 'name': 'Athens, Greece', 'coordinates': (37.975, 23.789),
             'country': 'GR', 'continent': 'Europe', 'active': True},
            {'site_id': 'seoul', 'name': 'Seoul, South Korea', 'coordinates': (37.58, 127.05),
             'country': 'KR', 'continent': 'Asia', 'active': True},
            # ... (other sites)
        ]
        
        if continent:
            sites_filtered = [s for s in all_sites if s['continent'].lower() == continent.lower()]
        else:
            sites_filtered = all_sites
            
        return {'results': sites_filtered, '_attribution': {'source': 'NASA Pandora Project (Mock List)'}}
        
    def _generate_mock_column_data(self, product: str) -> Dict[str, Any]:
        pass # Placeholder for brevity
    def _generate_mock_column_data(self, product: str) -> Dict[str, Any]:
        pass # Placeholder for brevity