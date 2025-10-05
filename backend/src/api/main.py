"""
Module: main
Description: FastAPI application entry point for NASA TEMPO Air Quality API
Integrates multiple data sources: TEMPO, OpenAQ, AirNow, PurpleAir, Pandora
"""

import logging
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

# Import data fetchers
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from data_ingestion.openaq_fetcher import OpenAQFetcher
from data_ingestion.pandora_fetcher import PandoraFetcher
from data_ingestion.data_attribution import get_attribution_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NASA TEMPO Air Quality API",
    description="Air quality forecasting using TEMPO satellite data and ground-based validation networks",
    version="0.2.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data fetchers
openaq_fetcher = OpenAQFetcher()
pandora_fetcher = PandoraFetcher()
attribution_manager = get_attribution_manager()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NASA TEMPO Air Quality Forecasting API",
        "version": "0.2.0",
        "docs": "/docs",
        "data_sources": ["TEMPO", "OpenAQ", "AirNow", "PurpleAir", "Pandora", "OpenWeather"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# ==================== OpenAQ Endpoints ====================

@app.get("/api/v1/openaq/latest")
async def get_openaq_latest(
    country: Optional[str] = Query(None, description="Two-letter country code"),
    city: Optional[str] = Query(None, description="City name"),
    latitude: Optional[float] = Query(None, description="Latitude for location search"),
    longitude: Optional[float] = Query(None, description="Longitude for location search"),
    radius: int = Query(25000, description="Search radius in meters"),
    parameter: Optional[str] = Query(None, description="Pollutant parameter (pm25, pm10, o3, no2, so2, co)"),
    limit: int = Query(100, le=1000, description="Maximum number of results")
):
    """
    Get latest air quality measurements from OpenAQ
    
    Example: /api/v1/openaq/latest?latitude=34.05&longitude=-118.24&parameter=pm25&radius=10000
    """
    try:
        coordinates = (latitude, longitude) if latitude and longitude else None
        
        data = openaq_fetcher.fetch_latest_measurements(
            country=country,
            city=city,
            coordinates=coordinates,
            radius=radius,
            parameter=parameter,
            limit=limit
        )
        
        # Log usage
        params = [parameter] if parameter else ['all']
        attribution_manager.log_usage(
            'OpenAQ',
            params,
            {'lat': latitude, 'lon': longitude} if coordinates else None,
            len(data.get('results', []))
        )
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching OpenAQ data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/openaq/locations")
async def get_openaq_locations(
    country: Optional[str] = Query(None, description="Two-letter country code"),
    city: Optional[str] = Query(None, description="City name"),
    latitude: Optional[float] = Query(None, description="Latitude"),
    longitude: Optional[float] = Query(None, description="Longitude"),
    radius: int = Query(25000, description="Search radius in meters"),
    limit: int = Query(100, le=1000, description="Maximum number of results")
):
    """Get available OpenAQ monitoring locations"""
    try:
        coordinates = (latitude, longitude) if latitude and longitude else None
        
        data = openaq_fetcher.fetch_locations(
            country=country,
            city=city,
            coordinates=coordinates,
            radius=radius,
            limit=limit
        )
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching OpenAQ locations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Pandora Endpoints ====================

@app.get("/api/v1/pandora/sites")
async def get_pandora_sites():
    """Get list of available Pandora monitoring sites"""
    try:
        data = pandora_fetcher.fetch_site_list()
        
        attribution_manager.log_usage('Pandora', ['site_list'], None, len(data['results']))
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching Pandora sites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/pandora/sites/{site_id}")
async def get_pandora_site_data(
    site_id: str,
    product: str = Query('NO2', description="Data product (NO2, O3, HCHO, SO2, AOD)"),
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Get column measurement data for a specific Pandora site
    
    Example: /api/v1/pandora/sites/maryland?product=NO2
    """
    try:
        date_obj = datetime.fromisoformat(date) if date else None
        
        data = pandora_fetcher.fetch_site_data(site_id, product, date_obj)
        
        attribution_manager.log_usage('Pandora', [product], None, 1)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching Pandora site data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/pandora/tempo-validation/{site_id}")
async def get_tempo_validation(
    site_id: str,
    date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")
):
    """
    Get Pandora ground measurements formatted for TEMPO satellite validation
    
    This endpoint is critical for satellite-ground comparison, a key requirement
    of the NASA Space Apps Challenge.
    """
    try:
        date_obj = datetime.fromisoformat(date) if date else None
        
        data = pandora_fetcher.fetch_comparison_with_tempo(site_id, date_obj)
        
        attribution_manager.log_usage('Pandora', ['NO2', 'O3'], None, 1)
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching TEMPO validation data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/pandora/nearby")
async def get_nearby_pandora_sites(
    latitude: float = Query(..., description="Latitude in degrees"),
    longitude: float = Query(..., description="Longitude in degrees"),
    radius_km: float = Query(100, description="Search radius in kilometers")
):
    """Find Pandora sites near a given location"""
    try:
        sites = pandora_fetcher.get_sites_near_location(latitude, longitude, radius_km)
        
        return {
            'query_location': {'latitude': latitude, 'longitude': longitude},
            'radius_km': radius_km,
            'sites_found': len(sites),
            'sites': sites
        }
        
    except Exception as e:
        logger.error(f"Error finding nearby Pandora sites: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Data Attribution Endpoints ====================

@app.get("/api/v1/attribution")
async def get_all_attributions():
    """
    Get attribution information for all data sources
    
    This endpoint fulfills the challenge requirement to cite all data sources.
    """
    try:
        return attribution_manager.get_all_attributions()
    except Exception as e:
        logger.error(f"Error getting attributions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/attribution/{source}")
async def get_source_attribution(source: str):
    """Get attribution information for a specific data source"""
    try:
        attribution = attribution_manager.get_attribution(source)
        if attribution is None:
            raise HTTPException(status_code=404, detail=f"Source '{source}' not found")
        return attribution
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting attribution for {source}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/attribution/web-display")
async def get_web_attribution(
    sources: Optional[List[str]] = Query(None, description="List of sources to include")
):
    """Get formatted attribution data for web display"""
    try:
        return attribution_manager.generate_web_attribution(sources)
    except Exception as e:
        logger.error(f"Error generating web attribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/attribution/citation")
async def get_citation_text(
    sources: Optional[List[str]] = Query(None, description="List of sources to include")
):
    """Get formatted citation text for all or specified data sources"""
    try:
        citation = attribution_manager.generate_citation_text(sources)
        return {"citation_text": citation}
    except Exception as e:
        logger.error(f"Error generating citation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/attribution/usage-summary")
async def get_usage_summary():
    """Get summary of data source usage during this session"""
    try:
        return attribution_manager.get_usage_summary()
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# TODO: Add additional API routers
# from .routes import air_quality, forecasts, alerts
# app.include_router(air_quality.router, prefix="/api/v1/air-quality")
# app.include_router(forecasts.router, prefix="/api/v1/forecasts")
# app.include_router(alerts.router, prefix="/api/v1/alerts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
