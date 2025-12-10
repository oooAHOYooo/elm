import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests

_logger = logging.getLogger(__name__)
_CACHE: Dict[str, Tuple[float, Any]] = {}


def _cache_get(key: str, ttl: int) -> Optional[Any]:
    item = _CACHE.get(key)
    if not item:
        return None
    ts, value = item
    if time.time() - ts > ttl:
        return None
    return value


def _cache_set(key: str, value: Any) -> None:
    _CACHE[key] = (time.time(), value)


def _format_date_param(day: str, tz_name: str = "America/New_York") -> str:
    """
    Return YYYYMMDD for 'today' or 'tomorrow' in local time.
    """
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = None
    now = datetime.now(tz) if tz else datetime.now()
    if day == "tomorrow":
        now = now + timedelta(days=1)
    return now.strftime("%Y%m%d")


def fetch_tides(
    station: str = "8465705",
    day: str = "today",
    units: str = "english",
    datum: str = "MLLW",
    ttl_seconds: int = 600,
) -> Dict[str, Any]:
    """
    Fetch today's or tomorrow's high/low tide predictions for a NOAA station.
    Returns dict with 'predictions': [{t, type, v}], where type is 'H' or 'L'.
    """
    key = f"tides:{station}:{day}:{units}:{datum}"
    cached = _cache_get(key, ttl_seconds)
    if cached is not None:
        return cached

    base = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
    date_str = _format_date_param(day)
    params = {
        "product": "predictions",
        "application": "ElmCityDaily",
        "begin_date": date_str,
        "end_date": date_str,
        "datum": datum,
        "station": station,
        "time_zone": "lst_ldt",
        "units": units,
        "interval": "hilo",
        "format": "json",
    }
    try:
        resp = requests.get(base, params=params, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        preds: List[Dict[str, Any]] = data.get("predictions", []) or []
        result = {
            "station": station,
            "date": date_str,
            "predictions": preds,
            "units": units,
            "datum": datum,
        }
        _cache_set(key, result)
        return result
    except Exception as err:
        _logger.error("Failed to fetch tides for station %s: %s", station, err)
        return {"station": station, "date": date_str, "predictions": [], "units": units, "datum": datum}



