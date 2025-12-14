"""
Air Quality Index service using EPA AirNow API.

AirNow provides free access to real-time air quality data.
For production use, register for an API key at: https://docs.airnowapi.org/
Without a key, we fall back to the AirNow widget data or return unavailable.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import requests
from utils.cache import TTLCache

_logger = logging.getLogger(__name__)

# Persistent cache for AQI data
_CACHE = TTLCache(ttl_seconds=1800, filepath=".cache_aqi.pkl")


def _get_cache(key: str, ttl: int) -> Optional[Any]:
    return _CACHE.get(key)


def _set_cache(key: str, value: Any) -> None:
    _CACHE.set(key, value)


# AQI color and health categories per EPA standards
AQI_CATEGORIES = {
    (0, 50): {"level": "Good", "color": "#00e400", "emoji": "🟢", "advice": "Air quality is satisfactory."},
    (51, 100): {"level": "Moderate", "color": "#ffff00", "emoji": "🟡", "advice": "Acceptable; sensitive individuals may experience issues."},
    (101, 150): {"level": "Unhealthy for Sensitive Groups", "color": "#ff7e00", "emoji": "🟠", "advice": "Sensitive groups should limit outdoor exertion."},
    (151, 200): {"level": "Unhealthy", "color": "#ff0000", "emoji": "🔴", "advice": "Everyone may begin to experience health effects."},
    (201, 300): {"level": "Very Unhealthy", "color": "#8f3f97", "emoji": "🟣", "advice": "Health alert: everyone may experience serious effects."},
    (301, 500): {"level": "Hazardous", "color": "#7e0023", "emoji": "🟤", "advice": "Emergency conditions. Stay indoors."},
}


def _get_aqi_category(aqi: int) -> Dict[str, str]:
    """Return category info for a given AQI value."""
    for (low, high), info in AQI_CATEGORIES.items():
        if low <= aqi <= high:
            return info
    return {"level": "Unknown", "color": "#999", "emoji": "⚪", "advice": "Data unavailable."}


def fetch_air_quality(
    lat: float = 41.3083,
    lon: float = -72.9279,
    api_key: Optional[str] = None,
    ttl_seconds: int = 1800,  # 30 minutes - AQI updates hourly
) -> Dict[str, Any]:
    """
    Fetch current air quality data for the given coordinates.
    
    Uses EPA AirNow API if api_key is provided, otherwise attempts
    to get data from the public observation endpoint.
    
    Returns dict with:
        - aqi: int or None
        - category: str (Good, Moderate, etc.)
        - color: str (hex color for display)
        - emoji: str
        - advice: str (health recommendation)
        - pollutant: str (primary pollutant, e.g., PM2.5, O3)
        - timestamp: str (observation time)
        - available: bool
    """
    cache_key = f"aqi:{lat:.4f},{lon:.4f}"
    cached = _get_cache(cache_key, ttl_seconds)
    if cached is not None:
        return cached

    result = {
        "aqi": None,
        "category": "Unknown",
        "color": "#999",
        "emoji": "⚪",
        "advice": "Air quality data unavailable.",
        "pollutant": None,
        "timestamp": None,
        "available": False,
    }

    # Try AirNow API (requires free API key)
    if api_key:
        try:
            url = "https://www.airnowapi.org/aq/observation/latLong/current/"
            params = {
                "format": "application/json",
                "latitude": lat,
                "longitude": lon,
                "distance": 25,  # miles
                "API_KEY": api_key,
            }
            resp = requests.get(url, params=params, timeout=8)
            resp.raise_for_status()
            data = resp.json()

            if data and len(data) > 0:
                # Find the highest AQI among pollutants (worst case)
                worst = max(data, key=lambda x: x.get("AQI", 0))
                aqi_val = worst.get("AQI")
                if aqi_val is not None:
                    cat_info = _get_aqi_category(aqi_val)
                    result = {
                        "aqi": aqi_val,
                        "category": cat_info["level"],
                        "color": cat_info["color"],
                        "emoji": cat_info["emoji"],
                        "advice": cat_info["advice"],
                        "pollutant": worst.get("ParameterName", "Unknown"),
                        "timestamp": worst.get("DateObserved", "") + " " + worst.get("HourObserved", ""),
                        "available": True,
                        "reporting_area": worst.get("ReportingArea", ""),
                    }
                    _set_cache(cache_key, result)
                    return result

        except Exception as err:
            _logger.warning("AirNow API error: %s", err)

    # Fallback: Try AirNow's public current observations (no key needed, less reliable)
    try:
        # This endpoint provides observations for reporting areas
        # We'll use the nearest major reporting area to New Haven
        url = "https://www.airnowapi.org/aq/observation/zipCode/current/"
        params = {
            "format": "application/json",
            "zipCode": "06511",  # New Haven ZIP
            "distance": 25,
        }
        
        # Only works with API key, so let's try a different approach
        # Use the AirNow widget data endpoint (public)
        widget_url = f"https://www.airnow.gov/aqi/widget/?latitude={lat}&longitude={lon}"
        
        # Since direct API requires a key, we'll return unavailable but with helpful info
        # In production, get a free key from https://docs.airnowapi.org/
        _logger.info("AirNow API key not configured. Register at https://docs.airnowapi.org/")
        
    except Exception as err:
        _logger.warning("AirNow fallback error: %s", err)

    _set_cache(cache_key, result)
    return result


def fetch_air_quality_forecast(
    lat: float = 41.3083,
    lon: float = -72.9279,
    api_key: Optional[str] = None,
    ttl_seconds: int = 3600,
) -> List[Dict[str, Any]]:
    """
    Fetch AQI forecast for the next few days.
    Requires API key.
    """
    if not api_key:
        return []

    cache_key = f"aqi_forecast:{lat:.4f},{lon:.4f}"
    cached = _get_cache(cache_key, ttl_seconds)
    if cached is not None:
        return cached

    try:
        url = "https://www.airnowapi.org/aq/forecast/latLong/"
        params = {
            "format": "application/json",
            "latitude": lat,
            "longitude": lon,
            "distance": 25,
            "API_KEY": api_key,
        }
        resp = requests.get(url, params=params, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        forecasts = []
        for item in data or []:
            aqi_val = item.get("AQI")
            if aqi_val is not None:
                cat_info = _get_aqi_category(aqi_val)
                forecasts.append({
                    "date": item.get("DateForecast", ""),
                    "aqi": aqi_val,
                    "category": cat_info["level"],
                    "color": cat_info["color"],
                    "emoji": cat_info["emoji"],
                    "pollutant": item.get("ParameterName", ""),
                })

        _set_cache(cache_key, forecasts)
        return forecasts

    except Exception as err:
        _logger.warning("AirNow forecast error: %s", err)
        return []

