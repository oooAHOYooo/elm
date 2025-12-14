import logging
import time
from typing import Any, Dict, List, Optional, Tuple

import feedparser
import requests
from utils.cache import TTLCache

_logger = logging.getLogger(__name__)

# Persistent cache for NWS data
# Use 15 min TTL default; alerts requests ask for 300s but TTLCache enforces one TTL.
# 900s (15m) is fine for alerts too, or we could lower it.
# Let's use 600s (10m) as a middle ground.
_CACHE = TTLCache(ttl_seconds=600, filepath=".cache_nws.pkl")
_UA = {"User-Agent": "ElmCityDaily/1.0 (+https://example.local)"}


def _get_cache(key: str, ttl: int) -> Optional[Any]:
    return _CACHE.get(key)


def _set_cache(key: str, value: Any) -> None:
    _CACHE.set(key, value)


def fetch_nws_alerts(zone: str = "ctz010", ttl_seconds: int = 300) -> List[Dict[str, Any]]:
    """
    Fetch active NWS alerts for the specified zone using CAP RSS.
    Example zone for New Haven: CTZ010.
    """
    key = f"nws_alerts:{zone}"
    cached = _get_cache(key, ttl_seconds)
    if cached is not None:
        return cached
    url = f"https://alerts.weather.gov/cap/{zone.lower()}.cap"
    try:
        parsed = feedparser.parse(url)
        alerts: List[Dict[str, Any]] = []
        for e in parsed.entries:
            alerts.append(
                {
                    "title": getattr(e, "title", "") or e.get("title", ""),
                    "summary": getattr(e, "summary", "") or e.get("summary", ""),
                    "link": getattr(e, "link", "") or e.get("link", ""),
                    "published": getattr(e, "published", "") or e.get("published", ""),
                    "severity": getattr(e, "cap_severity", "") or e.get("cap_severity", ""),
                    "event": getattr(e, "cap_event", "") or e.get("cap_event", ""),
                }
            )
        _set_cache(key, alerts)
        return alerts
    except Exception as err:
        _logger.error("Failed to fetch NWS alerts: %s", err)
        return []


def fetch_nws_forecast(lat: float, lon: float, ttl_seconds: int = 900) -> Dict[str, Any]:
    """
    Fetch NWS forecast and hourly forecast using the points API.
    Returns dict with 'periods' (from daily forecast) and 'hourly' (first 24 hours).
    """
    key = f"nws_forecast:{lat:.4f},{lon:.4f}"
    cached = _get_cache(key, ttl_seconds)
    if cached is not None:
        return cached
    try:
        points_url = f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}"
        points = requests.get(points_url, headers=_UA, timeout=6).json()
        forecast_url = points["properties"]["forecast"]
        hourly_url = points["properties"]["forecastHourly"]

        forecast = requests.get(forecast_url, headers=_UA, timeout=6).json()
        hourly = requests.get(hourly_url, headers=_UA, timeout=6).json()
        periods = forecast.get("properties", {}).get("periods", []) or []
        hourly_periods = hourly.get("properties", {}).get("periods", []) or []

        result = {
            "periods": [
                {
                    "name": p.get("name"),
                    "temperature": p.get("temperature"),
                    "temperatureUnit": p.get("temperatureUnit"),
                    "shortForecast": p.get("shortForecast"),
                    "detailedForecast": p.get("detailedForecast"),
                    "isDaytime": p.get("isDaytime"),
                }
                for p in periods
            ],
            "hourly": [
                {
                    "startTime": h.get("startTime"),
                    "temperature": h.get("temperature"),
                    "temperatureUnit": h.get("temperatureUnit"),
                    "shortForecast": h.get("shortForecast"),
                    "windSpeed": h.get("windSpeed"),
                }
                for h in hourly_periods[:24]
            ],
        }
        _set_cache(key, result)
        return result
    except Exception as err:
        _logger.error("Failed to fetch NWS forecast: %s", err)
        return {"periods": [], "hourly": []}


