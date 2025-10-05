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
from data_ingestion.tempo_fetcher import TEMPOFetcher
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
# TEMPO fetcher - Earthdata credentials may be provided via environment or netrc
tempo_fetcher = TEMPOFetcher()
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
            {'lat': coordinates[0], 'lon': coordinates[1]} if coordinates else None,
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


# ==================== TEMPO Endpoints ====================


@app.get("/api/v1/tempo/latest")
async def get_tempo_latest():
    """Get latest TEMPO granules (cached)"""
    try:
        data = tempo_fetcher.fetch_latest()

        # Log attribution usage
        attribution_manager.log_usage('TEMPO', ['NO2', 'O3', 'HCHO'], None, len(data.get('features', [])))

        return data

    except RuntimeError as re:
        logger.error(f"Runtime error fetching TEMPO latest: {re}")
        # Service unavailable due to missing credentials or client
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.error(f"Error fetching TEMPO latest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tempo/location")
async def get_tempo_location(
    lat: float = Query(..., description="Latitude in degrees"),
    lon: float = Query(..., description="Longitude in degrees"),
    radius_km: float = Query(10.0, description="Search radius in kilometers"),
    when: Optional[str] = Query(None, description="ISO datetime to search around (UTC)")
):
    """Get TEMPO granules near a location"""
    try:
        when_dt = datetime.fromisoformat(when) if when else None

        data = tempo_fetcher.fetch_by_location(lat, lon, radius_km, when_dt)

        attribution_manager.log_usage('TEMPO', ['NO2', 'O3', 'HCHO'], {'lat': lat, 'lon': lon}, len(data.get('features', [])))

        return data

    except ValueError as ve:
        logger.error(f"Invalid params for TEMPO location: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        logger.error(f"Runtime error fetching TEMPO by location: {re}")
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.error(f"Error fetching TEMPO by location: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tempo/timerange")
async def get_tempo_timerange(
    start: str = Query(..., description="Start ISO datetime (UTC)"),
    end: str = Query(..., description="End ISO datetime (UTC)"),
    min_lon: Optional[float] = Query(None),
    min_lat: Optional[float] = Query(None),
    max_lon: Optional[float] = Query(None),
    max_lat: Optional[float] = Query(None)
):
    """Get TEMPO granules for a time range and optional bbox"""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        bbox = None
        if all(x is not None for x in (min_lon, min_lat, max_lon, max_lat)):
            bbox = (float(min_lon), float(min_lat), float(max_lon), float(max_lat))  # type: ignore

        data = tempo_fetcher.fetch_timerange(start_dt, end_dt, bbox=bbox)

        attribution_manager.log_usage('TEMPO', ['NO2', 'O3', 'HCHO'], None, len(data.get('features', [])))

        return data

    except ValueError as ve:
        logger.error(f"Invalid params for TEMPO timerange: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        logger.error(f"Runtime error fetching TEMPO timerange: {re}")
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.error(f"Error fetching TEMPO timerange: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tempo/pollutant/{pollutant}")
async def get_tempo_pollutant(
    pollutant: str,
    start: Optional[str] = Query(None, description="Start ISO datetime (UTC)"),
    end: Optional[str] = Query(None, description="End ISO datetime (UTC)")
):
    """Get TEMPO data filtered by pollutant (NO2, O3, HCHO)"""
    try:
        start_dt = datetime.fromisoformat(start) if start else None
        end_dt = datetime.fromisoformat(end) if end else None

        data = tempo_fetcher.fetch_by_pollutant(pollutant, start=start_dt, end=end_dt)

        attribution_manager.log_usage('TEMPO', [pollutant.upper()], None, len(data.get('features', [])))

        return data

    except ValueError as ve:
        logger.error(f"Invalid pollutant request: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        logger.error(f"Runtime error fetching TEMPO pollutant data: {re}")
        raise HTTPException(status_code=503, detail=str(re))
    except Exception as e:
        logger.error(f"Error fetching TEMPO pollutant data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
