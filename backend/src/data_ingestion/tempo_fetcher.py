"""
Module: tempo_fetcher
Description: Fetches TEMPO satellite data from NASA Earthdata
Author: NASA Space Apps Team
Created: October 4, 2025
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
import os
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

try:
    # earthaccess is the recommended client for NASA Earthdata access
    import earthaccess
    from earthaccess import EarthdataSession
    from earthaccess import Search
    EARTHACCESS_AVAILABLE = True
except ImportError:
    EARTHACCESS_AVAILABLE = False
    # Define placeholders to avoid NameError
    EarthdataSession = None
    Search = None


class TEMPOFetcher:
    """
    TEMPO Satellite Data Fetcher using earthaccess

    Notes:
    - This class expects Earthdata credentials to be available via environment
      variables, netrc, or passed into an EarthdataSession (username/password).
    - The implementation uses a small in-memory cache for repeated requests.
    """

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None, cache_ttl_minutes: int = 15) -> None:
        """
        Initialize TEMPOFetcher

        Args:
            username: Earthdata username (optional if using netrc)
            password: Earthdata password (optional)
            cache_ttl_minutes: TTL for simple cache (not enforced by lru_cache, used in keying)
        """
        if not EARTHACCESS_AVAILABLE:
            logger.warning("earthaccess library not available. Install with `pip install earthaccess` to enable TEMPO fetching.")

        self.username = username
        self.password = password
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)

        # Create a session lazily to avoid requiring credentials at import time
        self._session = None
        logger.info(f"Initialized {self.__class__.__name__}")

    def _get_session(self) -> Optional[object]:
        """Create or return an existing EarthdataSession. Returns None if earthaccess not installed."""
        if not EARTHACCESS_AVAILABLE:
            return None
        if self._session is None:
            try:
                if self.username and self.password:
                    # Use provided credentials: create session then login
                    self._session = EarthdataSession() # type: ignore
                    # call login if available
                    try:
                        self._session.login(username=self.username, password=self.password)
                    except Exception:
                        # some versions might not support login; recreate with creds
                        self._session = EarthdataSession(username=self.username, password=self.password) # type: ignore
                else:
                    # Try to create a session relying on .netrc or env vars
                    # auth=True may be required by some earthaccess versions
                    try:
                        self._session = EarthdataSession(auth=True) # type: ignore
                    except TypeError:
                        # fallback if auth kw not accepted
                        self._session = EarthdataSession() # type: ignore

            except Exception as e:
                msg = (
                    "Failed to create EarthdataSession: {}.\n"
                    "Ensure you have an EarthData account and configured credentials.\n"
                    "Options:\n"
                    "  1) Create ~/.netrc with Earthdata credentials (machine urs.earthdata.nasa.gov login <user> password <pass>)\n"
                    "  2) Set environment variables EARTHDATA_USERNAME and EARTHDATA_PASSWORD\n"
                    "  3) Pass username/password to TEMPOFetcher(username, password)\n"
                ).format(repr(e))
                logger.error(msg)
                raise RuntimeError(msg)

        return self._session

    def _search_granules(self, start: datetime, end: datetime, bbox: Optional[Tuple[float, float, float, float]] = None, product_short_name: str = "TEMPO_L2") -> List[Dict[str, Any]]:
        """Search for TEMPO granules using earthaccess Search wrapper.

        Returns a list of granule metadata dictionaries.
        """
        session = self._get_session()
        if session is None:
            raise RuntimeError("earthaccess library is not installed or Earthdata credentials are not configured")

        try:
            search = Search(session=session) # type: ignore
            kwargs = {
                'short_name': product_short_name,
                'temporal': f"{start.isoformat()}Z,{end.isoformat()}Z",
            }
            if bbox:
                kwargs['bounding_box'] = ",".join(map(str, bbox))

            granules = list(search.granules(**kwargs))
            results = []
            for g in granules:
                try:
                    gd = {k: getattr(g, k) for k in ['id', 'title', 'updated', 'links'] if hasattr(g, k)}
                except Exception:
                    gd = {}
                results.append(gd)

            return results

        except Exception as e:
            logger.error(f"Error during granule search: {e}")
            raise

        # Use Search from earthaccess if available; keep code defensive in case API differs
        try:
            search = Search(session=session)
            # product_short_name chosen generically; real product names can be refined
            kwargs = {
                'short_name': product_short_name,
                'temporal': f"{start.isoformat()}Z,{end.isoformat()}Z",
            }
            if bbox:
                # bbox order: west,south,east,north
                kwargs['bounding_box'] = ",".join(map(str, bbox))

            granules = list(search.granules(**kwargs))
            results = []
            for g in granules:
                # earthaccess granule has attributes; convert to dict safely
                try:
                    gd = {k: getattr(g, k) for k in ['id', 'title', 'updated', 'links'] if hasattr(g, k)}
                except Exception:
                    gd = {}
                results.append(gd)

            return results

        except Exception as e:
            logger.error(f"Error during granule search: {e}")
            raise

    @lru_cache(maxsize=256)
    def fetch_latest(self) -> Dict[str, Any]:
        """Fetch the most recent TEMPO granules and return summarized JSON/GeoJSON.

        This method is cached via lru_cache to avoid repeated network calls.
        """
        end = datetime.utcnow()
        start = end - timedelta(hours=6)

        try:
            granules = self._search_granules(start, end)

            # Convert granule list into a simple GeoJSON FeatureCollection if location is available
            features = []
            for g in granules:
                props = {k: v for k, v in g.items() if k != 'links'}
                coords = None
                # Try to extract geometry from links if present (defensive)
                if 'links' in g and isinstance(g['links'], list):
                    # Not all granules have geometry in links; skip if absent
                    coords = None

                features.append({
                    'type': 'Feature',
                    'properties': props,
                    'geometry': None
                })

            result = {
                'type': 'FeatureCollection',
                'features': features,
                'fetched_at': datetime.utcnow().isoformat()
            }

            logger.info(f"Fetched {len(features)} TEMPO granules (latest)")
            return result

        except Exception as e:
            logger.error(f"fetch_latest failed: {e}")
            raise

    def fetch_by_location(self, lat: float, lon: float, radius_km: float = 10.0, when: Optional[datetime] = None) -> Dict[str, Any]:
        """Fetch TEMPO granules near a location. Returns GeoJSON-like dict.

        Args:
            lat, lon: center point
            radius_km: search radius in kilometers
            when: optional datetime to search around (defaults to now)
        """
        when = when or datetime.utcnow()
        # Create a small bbox around lat/lon based on radius
        # Approx conversion: 1 deg lat ~ 111 km
        d_deg = radius_km / 111.0
        bbox = (lon - d_deg, lat - d_deg, lon + d_deg, lat + d_deg)

        try:
            granules = self._search_granules(when - timedelta(hours=3), when + timedelta(hours=3), bbox=bbox)

            features = []
            for g in granules:
                features.append({'type': 'Feature', 'properties': g, 'geometry': None})

            return {'type': 'FeatureCollection', 'features': features, 'query': {'lat': lat, 'lon': lon, 'radius_km': radius_km}}

        except Exception as e:
            logger.error(f"fetch_by_location failed: {e}")
            raise

    def fetch_timerange(self, start: datetime, end: datetime, bbox: Optional[Tuple[float, float, float, float]] = None) -> Dict[str, Any]:
        """Fetch TEMPO granules for a time range and optional bbox."""
        if end < start:
            raise ValueError("end must be after start")

        try:
            granules = self._search_granules(start, end, bbox=bbox)
            return {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': g, 'geometry': None} for g in granules], 'start': start.isoformat(), 'end': end.isoformat()}

        except Exception as e:
            logger.error(f"fetch_timerange failed: {e}")
            raise

    def fetch_by_pollutant(self, pollutant: str, start: Optional[datetime] = None, end: Optional[datetime] = None) -> Dict[str, Any]:
        """Fetch TEMPO data granules filtered by pollutant/product.

        The pollutant product naming depends on TEMPO product short names; this
        method maps common pollutant names to likely product identifiers.
        """
        start = start or (datetime.utcnow() - timedelta(days=1))
        end = end or datetime.utcnow()

        product_map = {
            'NO2': 'TEMPO_L2_NO2',
            'O3': 'TEMPO_L2_O3',
            'HCHO': 'TEMPO_L2_HCHO'
        }

        pname = product_map.get(pollutant.upper(), None)
        if pname is None:
            raise ValueError(f"Unsupported pollutant: {pollutant}. Supported: {', '.join(product_map.keys())}")

        try:
            granules = self._search_granules(start, end, product_short_name=pname)
            return {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': g, 'geometry': None} for g in granules], 'pollutant': pollutant.upper()}

        except Exception as e:
            logger.error(f"fetch_by_pollutant failed: {e}")
            raise

