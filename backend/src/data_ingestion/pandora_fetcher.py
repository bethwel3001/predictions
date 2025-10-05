"""
Module: pandora_fetcher
Description: Fetches atmospheric column measurements from NASA's Pandora Project
Author: NASA Space Apps Team
Created: October 4, 2025 (Modified for E-A-A focus)

NASA's Pandora Project provides ground-based column measurements of trace gases
including NO2, O3, HCHO, and aerosols for satellite validation.
Website: https://pandora.gsfc.nasa.gov/
Data Access: https://data.pandonia-global-network.org
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
import ftplib
import io
import json # Added for continent filtering logic

logger = logging.getLogger(__name__)


class PandoraFetcher:
    """
    NASA Pandora Project Data Fetcher
    
    Fetches ground-based column measurements of atmospheric trace gases
    and aerosols from the Pandora network.
    """
    
    def __init__(self) -> None:
        """Initialize PandoraFetcher"""
        self.base_url = "https://data.pandonia-global-network.org"
        self.ftp_host = "data.pandonia-global-network.org"
        self.data_products = {
            'NO2': 'Nitrogen Dioxide column',
            'O3': 'Ozone column',
            'HCHO': 'Formaldehyde column',
            'SO2': 'Sulfur Dioxide column',
            'AOD': 'Aerosol Optical Depth'
        }
        
        # Define continents for easy filtering
        self.target_continents = ['Europe', 'Africa', 'Asia']
        
        logger.info(f"Initialized {self.__class__.__name__}")

    # --- MODIFIED METHOD ---
    def fetch_site_list(self, continent: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetch list of active Pandora monitoring sites, optionally filtered by continent.
        
        Args:
            continent: Optional filter ('Europe', 'Africa', 'Asia').
            
        Returns:
            Dictionary containing site information with coordinates.
            
        Note:
            This list is compiled from public Pandonia Global Network
            reports and is used for demonstration/mock purposes.
        """
        try:
            # PGN Sites focused on Europe, Africa, and Asia with coordinates
            all_sites = [
                # --- Europe ---
                {
                    'site_id': 'athens', 'name': 'Athens, Greece', 'coordinates': (37.975, 23.789),
                    'country': 'GR', 'continent': 'Europe', 'elevation': 212, 'active': True
                },
                {
                    'site_id': 'innsbruck', 'name': 'Innsbruck, Austria', 'coordinates': (47.268, 11.393),
                    'country': 'AT', 'continent': 'Europe', 'elevation': 577, 'active': True
                },
                {
                    'site_id': 'bremen', 'name': 'Bremen, Germany', 'coordinates': (53.100, 8.850),
                    'country': 'DE', 'continent': 'Europe', 'elevation': 3, 'active': True
                },
                {
                    'site_id': 'rome', 'name': 'Rome, Italy', 'coordinates': (41.815, 12.648),
                    'country': 'IT', 'continent': 'Europe', 'elevation': 125, 'active': True
                },
                # --- Africa ---
                {
                    'site_id': 'morocco_saidia', 'name': 'Saïdia, Morocco', 'coordinates': (35.08, -2.31),
                    'country': 'MA', 'continent': 'Africa', 'elevation': 10, 'active': True
                },
                # --- Asia ---
                {
                    'site_id': 'seoul', 'name': 'Seoul, South Korea', 'coordinates': (37.58, 127.05),
                    'country': 'KR', 'continent': 'Asia', 'elevation': 78, 'active': True
                },
                {
                    'site_id': 'beijing', 'name': 'Beijing, China', 'coordinates': (39.977, 116.381),
                    'country': 'CN', 'continent': 'Asia', 'elevation': 31, 'active': True
                },
                {
                    'site_id': 'manila', 'name': 'Manila Observatory, Philippines', 'coordinates': (14.637, 121.077),
                    'country': 'PH', 'continent': 'Asia', 'elevation': 35, 'active': True
                },
                {
                    'site_id': 'bangkok', 'name': 'Bangkok, Thailand', 'coordinates': (13.75, 100.5),
                    'country': 'TH', 'continent': 'Asia', 'elevation': 14, 'active': True
                },
                {
                    'site_id': 'seosan', 'name': 'Seosan, South Korea', 'coordinates': (36.8, 126.4),
                    'country': 'KR', 'continent': 'Asia', 'elevation': 10, 'active': True
                },
                {
                    'site_id': 'singapore', 'name': 'Singapore', 'coordinates': (1.35, 103.8),
                    'country': 'SG', 'continent': 'Asia', 'elevation': 15, 'active': True
                }
            ]
            
            # Apply continent filter
            if continent:
                if continent not in self.target_continents:
                    logger.warning(f"Invalid continent filter: {continent}. Returning all filtered sites.")
                    sites_filtered = [s for s in all_sites if s['continent'] in self.target_continents]
                else:
                    sites_filtered = [s for s in all_sites if s['continent'].lower() == continent.lower()]
            else:
                # Default to the target continents if no specific filter is provided
                sites_filtered = [s for s in all_sites if s['continent'] in self.target_continents]
            
            sites = {
                'results': sites_filtered,
                '_attribution': {
                    'source': 'NASA Pandora Project (PGN)',
                    'network': 'Pandonia Global Network',
                    'url': 'https://pandora.gsfc.nasa.gov/',
                    'data_url': 'https://data.pandonia-global-network.org',
                    'fetched_at': datetime.utcnow().isoformat(),
                    'data_note': 'Site coordinates are approximate/representative based on public PGN information.'
                }
            }
            
            logger.info(f"Retrieved {len(sites['results'])} Pandora sites (filtered for {continent if continent else 'E/A/A'})")
            return sites
            
        except Exception as e:
            logger.error(f"Error fetching Pandora site list: {e}")
            raise

    # --- NEW UTILITY METHOD ---
    def fetch_continent_data(
        self,
        continent: str,
        product: str = 'NO2',
        date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch column measurement data for all Pandora sites in a given continent.
        
        Args:
            continent: Continent to filter sites by ('Europe', 'Africa', 'Asia').
            product: Data product (NO2, O3, HCHO, SO2, AOD).
            date: Date for data retrieval (default: today).
            
        Returns:
            List of dictionaries, each containing data for a site.
        """
        if continent not in self.target_continents:
            raise ValueError(f"Continent must be one of: {self.target_continents}")
            
        logger.info(f"Starting batch fetch for {product} data in {continent}")
        
        sites_list = self.fetch_site_list(continent=continent)['results']
        continent_data = []
        
        for site in sites_list:
            site_id = site['site_id']
            try:
                # Fetch data for the specific site
                data = self.fetch_site_data(site_id, product, date)
                # Attach site metadata for completeness
                data['site_metadata'] = {
                    'name': site['name'],
                    'coordinates': site['coordinates'],
                    'country': site['country'],
                    'continent': site['continent']
                }
                continent_data.append(data)
                logger.info(f"-> Successfully fetched {product} for {site_id}")
            except Exception as e:
                logger.warning(f"-> Failed to fetch {product} data for {site_id}: {e}")
                
        logger.info(f"Batch fetch complete. Retrieved data from {len(continent_data)}/{len(sites_list)} sites.")
        return continent_data

    
    def fetch_site_data(
        self,
        site_id: str,
        product: str = 'NO2',
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch column measurement data for a specific Pandora site
        (Implementation is kept as a mock as the actual data retrieval
        requires a complex FTP/API interaction.)
        """
        try:
            if date is None:
                date = datetime.utcnow()
            
            if product not in self.data_products:
                raise ValueError(f"Product must be one of: {list(self.data_products.keys())}")
            
            logger.info(f"Fetching Pandora {product} data for site {site_id} on {date.date()}")
            
            # Mock data structure based on Pandora L2 format
            mock_data = {
                'site_id': site_id,
                'product': product,
                'product_description': self.data_products[product],
                'date': date.date().isoformat(),
                'measurements': self._generate_mock_column_data(product),
                'quality_flag': 0,
                'instrument': 'Pandora-2S',
                'data_level': 'L2',
                '_attribution': {
                    'source': 'NASA Pandora Project',
                    'citation': 'Pandora Project, NASA GSFC',
                    'url': 'https://pandora.gsfc.nasa.gov/',
                    'license': 'Public Domain',
                    'fetched_at': datetime.utcnow().isoformat()
                }
            }
            
            logger.info(f"Successfully retrieved Pandora data for {site_id} (MOCK)")
            return mock_data
            
        except Exception as e:
            logger.error(f"Error fetching Pandora site data: {e}")
            raise
    
    def fetch_comparison_with_tempo(
        self,
        site_id: str,
        date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Fetch Pandora ground measurements for TEMPO satellite validation
        """
        try:
            if date is None:
                date = datetime.utcnow()
            
            logger.info(f"Fetching Pandora-TEMPO comparison data for {site_id}")
            
            # Fetch NO2 and O3 columns (primary TEMPO products)
            no2_data = self.fetch_site_data(site_id, 'NO2', date)
            o3_data = self.fetch_site_data(site_id, 'O3', date)
            
            comparison = {
                'site_id': site_id,
                'date': date.date().isoformat(),
                'purpose': 'TEMPO satellite validation',
                'ground_measurements': {
                    'NO2': no2_data['measurements'],
                    'O3': o3_data['measurements']
                },
                'validation_notes': (
                    'Pandora provides direct-sun column measurements used to validate '
                    'TEMPO tropospheric column retrievals. Comparison requires temporal '
                    'averaging and air mass factor corrections.'
                ),
                '_attribution': {
                    'source': 'NASA Pandora Project',
                    'purpose': 'TEMPO satellite validation',
                    'url': 'https://pandora.gsfc.nasa.gov/',
                    'fetched_at': datetime.utcnow().isoformat()
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error in TEMPO comparison: {e}")
            raise
    
    def _generate_mock_column_data(self, product: str) -> Dict[str, Any]:
        """
        Generate mock column measurement data
        """
        column_values = {
            'NO2': 2.5e15,  # Typical tropospheric column (molecules/cm²)
            'O3': 8.5e18,   # Total column (molecules/cm²)
            'HCHO': 5.0e15, # Tropospheric column (molecules/cm²)
            'SO2': 1.0e15,  # Background level (molecules/cm²)
            'AOD': 0.15     # Aerosol optical depth (unitless)
        }
        
        return {
            'column_amount': column_values.get(product, 0.0),
            'unit': 'molecules/cm²' if product != 'AOD' else 'unitless',
            'uncertainty': column_values.get(product, 0.0) * 0.1,  # ~10% uncertainty
            'measurement_time': datetime.utcnow().isoformat(),
            'solar_zenith_angle': 45.0,
            'cloud_fraction': 0.1
        }
    
    def get_sites_near_location(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100
    ) -> List[Dict[str, Any]]:
        """
        Find Pandora sites within radius of given coordinates
        """
        try:
            from math import radians, cos, sin, asin, sqrt
            
            def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
                """Calculate distance between two points on Earth"""
                lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
                dlon = lon2 - lon1
                dlat = lat2 - lat1
                a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                c = 2 * asin(sqrt(a))
                km = 6371 * c
                return km
            
            # Fetch ALL sites in E/A/A
            sites_data = self.fetch_site_list(continent=None)
            nearby_sites = []
            
            for site in sites_data['results']:
                site_lat, site_lon = site['coordinates']
                distance = haversine(longitude, latitude, site_lon, site_lat)
                
                if distance <= radius_km:
                    site_with_distance = site.copy()
                    site_with_distance['distance_km'] = round(distance, 2)
                    nearby_sites.append(site_with_distance)
            
            # Sort by distance
            nearby_sites.sort(key=lambda x: x['distance_km'])
            
            logger.info(f"Found {len(nearby_sites)} Pandora sites within {radius_km}km (from E/A/A list)")
            return nearby_sites
            
        except Exception as e:
            logger.error(f"Error finding nearby sites: {e}")
            raise

if __name__ == '__main__':
    # Simple demonstration of the new functionality
    logging.basicConfig(level=logging.INFO)
    fetcher = PandoraFetcher()
    
    # 1. Fetch sites in Asia
    asia_sites = fetcher.fetch_site_list(continent='Asia')
    print("\n--- Asia Pandora Sites ---")
    print(json.dumps(asia_sites['results'], indent=2))
    
    # 2. Fetch NO2 data for all European sites
    europe_no2_data = fetcher.fetch_continent_data(continent='Europe', product='NO2')
    print("\n--- European NO2 Data (Mock) ---")
    for data in europe_no2_data:
        print(f"Site: {data['site_metadata']['name']} ({data['site_id']}) - "
              f"NO2 Column: {data['measurements']['column_amount']:.2e} {data['measurements']['unit']}")
    
    # 3. Find sites near a test location (e.g., Cairo, Egypt - Africa)
    cairo_lat, cairo_lon = 30.044, 31.235
    nearby_africa = fetcher.get_sites_near_location(cairo_lat, cairo_lon, radius_km=5000)
    print("\n--- Sites Near Cairo (5000km radius) ---")
    for site in nearby_africa:
        print(f"Site: {site['name']} ({site['continent']}) - Distance: {site['distance_km']} km")