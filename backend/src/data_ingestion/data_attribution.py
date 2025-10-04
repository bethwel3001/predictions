"""
Module: data_attribution
Description: Data source tracking and attribution system for NASA Space Apps Challenge
Author: NASA Space Apps Team
Created: October 4, 2025

This module ensures proper citation and attribution of all data sources used
in the TEMPO Air Quality Forecasting Platform, as required by the challenge.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    """Types of data sources used in the platform"""
    SATELLITE = "satellite"
    GROUND_STATION = "ground_station"
    SENSOR_NETWORK = "sensor_network"
    WEATHER = "weather"
    MODEL = "model"
    API = "api"


@dataclass
class DataAttribution:
    """
    Data attribution metadata for a single data source
    
    Attributes:
        source_name: Name of the data source
        source_type: Type of data source
        url: Primary URL for the data source
        citation: Formal citation text
        license: License type (e.g., 'CC BY 4.0', 'Public Domain')
        description: Brief description of the data
        parameters: List of parameters/pollutants provided
        coverage: Geographic or temporal coverage description
        fetched_at: Timestamp when data was retrieved
        additional_info: Optional additional attribution information
    """
    source_name: str
    source_type: DataSourceType
    url: str
    citation: str
    license: str
    description: str
    parameters: List[str]
    coverage: str
    fetched_at: str
    additional_info: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        result = asdict(self)
        result['source_type'] = self.source_type.value
        return result


class AttributionManager:
    """
    Manager for tracking and generating attribution information
    for all data sources used in the platform
    """
    
    def __init__(self) -> None:
        """Initialize AttributionManager with predefined source metadata"""
        self.sources = self._initialize_sources()
        self.usage_log: List[Dict[str, Any]] = []
        logger.info("Initialized AttributionManager")
    
    def _initialize_sources(self) -> Dict[str, DataAttribution]:
        """Initialize metadata for all supported data sources"""
        sources = {
            'TEMPO': DataAttribution(
                source_name='NASA TEMPO Mission',
                source_type=DataSourceType.SATELLITE,
                url='https://tempo.si.edu/',
                citation='NASA Tropospheric Emissions: Monitoring of Pollution (TEMPO)',
                license='Public Domain',
                description='Hourly satellite measurements of North American air quality',
                parameters=['NO2', 'O3', 'HCHO', 'CHOCHO', 'SO2', 'Aerosols'],
                coverage='North America, hourly daytime measurements',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'mission': 'TEMPO',
                    'agency': 'NASA',
                    'instrument': 'UV-Visible Spectrometer',
                    'resolution': '2.1 km x 4.4 km at center'
                }
            ),
            'OpenAQ': DataAttribution(
                source_name='OpenAQ',
                source_type=DataSourceType.SENSOR_NETWORK,
                url='https://openaq.org',
                citation='OpenAQ: Open Air Quality Data',
                license='CC BY 4.0',
                description='Global air quality data from government monitoring stations',
                parameters=['PM2.5', 'PM10', 'O3', 'NO2', 'SO2', 'CO'],
                coverage='Global, thousands of monitoring stations',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'data_sources': 'Government agencies and research institutions',
                    'aggregation': 'Real-time and historical data'
                }
            ),
            'AirNow': DataAttribution(
                source_name='EPA AirNow',
                source_type=DataSourceType.GROUND_STATION,
                url='https://www.airnow.gov/',
                citation='U.S. EPA AirNow Program',
                license='Public Domain',
                description='Real-time air quality data from EPA monitoring network',
                parameters=['O3', 'PM2.5', 'PM10', 'AQI'],
                coverage='United States, real-time and forecast',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'agency': 'U.S. Environmental Protection Agency',
                    'network': 'National air monitoring network',
                    'update_frequency': 'Hourly'
                }
            ),
            'PurpleAir': DataAttribution(
                source_name='PurpleAir',
                source_type=DataSourceType.SENSOR_NETWORK,
                url='https://www2.purpleair.com/',
                citation='PurpleAir: Community Air Quality Monitoring',
                license='Varies by sensor owner',
                description='Community-operated low-cost PM sensor network',
                parameters=['PM2.5', 'PM10'],
                coverage='Global, high-density in urban areas',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'sensor_type': 'PurpleAir PA-II',
                    'network_size': '20,000+ sensors',
                    'data_quality': 'Community-maintained, variable quality'
                }
            ),
            'Pandora': DataAttribution(
                source_name='NASA Pandora Project',
                source_type=DataSourceType.GROUND_STATION,
                url='https://pandora.gsfc.nasa.gov/',
                citation='NASA Pandora Project, Goddard Space Flight Center',
                license='Public Domain',
                description='Ground-based column measurements for satellite validation',
                parameters=['NO2', 'O3', 'HCHO', 'SO2', 'AOD'],
                coverage='Global network, ~100 sites',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'agency': 'NASA',
                    'purpose': 'Satellite validation (TEMPO, TROPOMI, OMI)',
                    'instrument': 'Pandora spectrometer systems',
                    'data_level': 'L2 total column amounts'
                }
            ),
            'OpenWeather': DataAttribution(
                source_name='OpenWeatherMap',
                source_type=DataSourceType.WEATHER,
                url='https://openweathermap.org/',
                citation='OpenWeatherMap Weather Data',
                license='ODbL (Open Database License)',
                description='Weather data including meteorological parameters',
                parameters=['Temperature', 'Humidity', 'Wind', 'Pressure', 'Clouds'],
                coverage='Global',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'data_sources': 'Weather stations, satellites, radar',
                    'update_frequency': 'Real-time'
                }
            ),
            'TolNet': DataAttribution(
                source_name='TOLNet',
                source_type=DataSourceType.GROUND_STATION,
                url='https://www-air.larc.nasa.gov/missions/TOLNet/',
                citation='NASA Tropospheric Ozone Lidar Network (TOLNet)',
                license='Public Domain',
                description='Ground-based lidar network for ozone profiling',
                parameters=['O3 vertical profiles'],
                coverage='North America, ~10 sites',
                fetched_at=datetime.utcnow().isoformat(),
                additional_info={
                    'agency': 'NASA',
                    'instrument': 'Ozone Lidar',
                    'purpose': 'Satellite validation and air quality research'
                }
            )
        }
        
        return sources
    
    def log_usage(
        self,
        source_key: str,
        parameters: List[str],
        location: Optional[Dict[str, float]] = None,
        record_count: Optional[int] = None
    ) -> None:
        """
        Log data source usage
        
        Args:
            source_key: Key identifying the data source
            parameters: List of parameters retrieved
            location: Optional location dictionary with lat/lon
            record_count: Number of records retrieved
        """
        if source_key not in self.sources:
            logger.warning(f"Unknown data source: {source_key}")
            return
        
        usage_entry = {
            'source': source_key,
            'timestamp': datetime.utcnow().isoformat(),
            'parameters': parameters,
            'location': location,
            'record_count': record_count
        }
        
        self.usage_log.append(usage_entry)
        logger.info(f"Logged usage of {source_key} data source")
    
    def get_attribution(self, source_key: str) -> Optional[Dict[str, Any]]:
        """
        Get attribution information for a specific data source
        
        Args:
            source_key: Key identifying the data source
            
        Returns:
            Dictionary with attribution metadata or None if not found
        """
        if source_key not in self.sources:
            logger.warning(f"Unknown data source: {source_key}")
            return None
        
        return self.sources[source_key].to_dict()
    
    def get_all_attributions(self) -> List[Dict[str, Any]]:
        """
        Get attribution information for all data sources
        
        Returns:
            List of dictionaries with attribution metadata for all sources
        """
        return [source.to_dict() for source in self.sources.values()]
    
    def generate_citation_text(
        self,
        sources_used: Optional[List[str]] = None
    ) -> str:
        """
        Generate formatted citation text for all or specified data sources
        
        Args:
            sources_used: Optional list of source keys to include.
                         If None, includes all sources.
        
        Returns:
            Formatted citation text
        """
        if sources_used is None:
            sources_used = list(self.sources.keys())
        
        citations = []
        citations.append("Data Sources:\n")
        
        for source_key in sources_used:
            if source_key in self.sources:
                source = self.sources[source_key]
                citations.append(
                    f"- {source.source_name}: {source.citation}\n"
                    f"  URL: {source.url}\n"
                    f"  License: {source.license}\n"
                )
        
        return "\n".join(citations)
    
    def generate_web_attribution(
        self,
        sources_used: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate attribution data formatted for web display
        
        Args:
            sources_used: Optional list of source keys to include
            
        Returns:
            Dictionary with formatted attribution for web display
        """
        if sources_used is None:
            # Get sources that have been used (logged)
            sources_used = list(set([entry['source'] for entry in self.usage_log]))
            if not sources_used:
                sources_used = list(self.sources.keys())
        
        web_attribution = {
            'title': 'Data Sources & Attribution',
            'description': (
                'This application uses data from multiple sources to provide '
                'comprehensive air quality forecasting. All data sources are '
                'acknowledged below with appropriate citations and licenses.'
            ),
            'sources': [],
            'generated_at': datetime.utcnow().isoformat()
        }
        
        for source_key in sources_used:
            if source_key in self.sources:
                source = self.sources[source_key]
                web_attribution['sources'].append({
                    'name': source.source_name,
                    'type': source.source_type.value,
                    'url': source.url,
                    'description': source.description,
                    'citation': source.citation,
                    'license': source.license,
                    'parameters': source.parameters,
                    'coverage': source.coverage
                })
        
        return web_attribution
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """
        Get summary of data source usage during this session
        
        Returns:
            Dictionary with usage statistics
        """
        usage_by_source = {}
        
        for entry in self.usage_log:
            source = entry['source']
            if source not in usage_by_source:
                usage_by_source[source] = {
                    'calls': 0,
                    'total_records': 0,
                    'parameters_used': set()
                }
            
            usage_by_source[source]['calls'] += 1
            if entry['record_count']:
                usage_by_source[source]['total_records'] += entry['record_count']
            usage_by_source[source]['parameters_used'].update(entry['parameters'])
        
        # Convert sets to lists for JSON serialization
        for source in usage_by_source:
            usage_by_source[source]['parameters_used'] = list(
                usage_by_source[source]['parameters_used']
            )
        
        return {
            'total_calls': len(self.usage_log),
            'sources_used': len(usage_by_source),
            'usage_by_source': usage_by_source,
            'session_start': (
                self.usage_log[0]['timestamp'] if self.usage_log else None
            ),
            'last_access': (
                self.usage_log[-1]['timestamp'] if self.usage_log else None
            )
        }


# Global attribution manager instance
_attribution_manager = None


def get_attribution_manager() -> AttributionManager:
    """
    Get the global AttributionManager instance
    
    Returns:
        Global AttributionManager instance (singleton pattern)
    """
    global _attribution_manager
    if _attribution_manager is None:
        _attribution_manager = AttributionManager()
    return _attribution_manager
