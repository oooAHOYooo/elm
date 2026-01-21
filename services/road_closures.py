"""
Road closure and construction alerts service for New Haven, CT.

Fetches data from CTroads Events API and CTDOT sources.
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import requests
from utils.cache import TTLCache

_logger = logging.getLogger(__name__)

# Cache for road closure data (1 hour TTL - closures don't change that frequently)
_CACHE = TTLCache(ttl_seconds=3600, filepath=".cache_road_closures.pkl")

# New Haven approximate bounding box for filtering
NH_BOUNDS = {
    "min_lat": 41.25,
    "max_lat": 41.35,
    "min_lon": -72.98,
    "max_lon": -72.88,
}

# New Haven area keywords for filtering
NH_KEYWORDS = [
    "new haven",
    "newhaven",
    "i-95",
    "i-91",
    "route 1",
    "route 34",
    "whalley",
    "chapel",
    "state street",
    "downtown new haven",
]


def _is_in_new_haven(road_name: str, lat: Optional[float] = None, lon: Optional[float] = None) -> bool:
    """Check if a road closure is in New Haven area."""
    road_lower = road_name.lower() if road_name else ""
    
    # Check keywords
    for keyword in NH_KEYWORDS:
        if keyword in road_lower:
            return True
    
    # Check bounding box if coordinates provided
    if lat and lon:
        if NH_BOUNDS["min_lat"] <= lat <= NH_BOUNDS["max_lat"]:
            if NH_BOUNDS["min_lon"] <= lon <= NH_BOUNDS["max_lon"]:
                return True
    
    return False


def fetch_ctroads_events(timeout: int = 8) -> List[Dict[str, Any]]:
    """
    Fetch road closure events from CTroads Events API.
    
    Returns list of events filtered for New Haven area.
    """
    cache_key = "ctroads_events"
    cached = _CACHE.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        # CTroads Events API endpoint
        url = "https://ctroads.org/api/v2/get/event"
        params = {
            "format": "json",
        }
        
        headers = {
            "User-Agent": "ElmCityDaily/1.0 (+https://elmcitydaily.com)",
            "Accept": "application/json",
        }
        
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        
        # Parse events
        events: List[Dict[str, Any]] = []
        
        # The API structure may vary - handle different response formats
        if isinstance(data, dict):
            # Try common response formats
            event_list = data.get("events") or data.get("data") or data.get("items") or []
        elif isinstance(data, list):
            event_list = data
        else:
            event_list = []
        
        now = datetime.now(ZoneInfo("America/New_York"))
        
        for event in event_list:
            if not isinstance(event, dict):
                continue
            
            # Extract relevant fields
            road_name = event.get("RoadwayName") or event.get("roadway") or event.get("road") or ""
            event_type = event.get("EventSubType") or event.get("type") or event.get("event_type") or ""
            is_full_closure = event.get("IsFullClosure") or event.get("is_full_closure") or False
            description = event.get("Description") or event.get("description") or event.get("message") or ""
            
            # Try to get dates
            start_time = None
            end_time = None
            
            # Try various date field names
            for date_field in ["StartTime", "start_time", "StartDate", "start_date", "EventStart"]:
                if date_field in event and event[date_field]:
                    try:
                        if isinstance(event[date_field], str):
                            # Try parsing ISO format or other common formats
                            start_time = datetime.fromisoformat(event[date_field].replace("Z", "+00:00"))
                        elif isinstance(event[date_field], (int, float)):
                            # Unix timestamp
                            start_time = datetime.fromtimestamp(event[date_field], tz=ZoneInfo("America/New_York"))
                    except Exception:
                        pass
                    if start_time:
                        break
            
            for date_field in ["EndTime", "end_time", "EndDate", "end_date", "EventEnd"]:
                if date_field in event and event[date_field]:
                    try:
                        if isinstance(event[date_field], str):
                            end_time = datetime.fromisoformat(event[date_field].replace("Z", "+00:00"))
                        elif isinstance(event[date_field], (int, float)):
                            end_time = datetime.fromtimestamp(event[date_field], tz=ZoneInfo("America/New_York"))
                    except Exception:
                        pass
                    if end_time:
                        break
            
            # Get coordinates if available
            lat = event.get("Latitude") or event.get("lat") or event.get("y")
            lon = event.get("Longitude") or event.get("lon") or event.get("x")
            
            # Filter for New Haven area
            if not _is_in_new_haven(road_name, lat, lon):
                continue
            
            # Only include future or current events (within next 7 days)
            if start_time:
                if start_time > now + timedelta(days=7):
                    continue  # Too far in future
            elif end_time:
                if end_time < now:
                    continue  # Already ended
            
            # Normalize event
            normalized = {
                "road": road_name,
                "type": event_type or "Road Work",
                "is_full_closure": bool(is_full_closure),
                "description": description,
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
                "start_display": start_time.strftime("%b %d, %I:%M %p") if start_time else "Ongoing",
                "end_display": end_time.strftime("%b %d, %I:%M %p") if end_time else "Until further notice",
                "source": "CTroads",
            }
            
            events.append(normalized)
        
        # Sort by start time (soonest first)
        events.sort(key=lambda x: x.get("start_time") or "9999", reverse=False)
        
        _CACHE.set(cache_key, events)
        return events
        
    except requests.exceptions.RequestException as e:
        _logger.warning(f"Failed to fetch CTroads events: {e}")
        _CACHE.set(cache_key, [])
        return []
    except Exception as e:
        _logger.error(f"Error parsing CTroads events: {e}")
        _CACHE.set(cache_key, [])
        return []


def fetch_road_closures(timeout: int = 8) -> List[Dict[str, Any]]:
    """
    Fetch all road closures from available sources.
    
    Currently uses CTroads Events API. Can be extended to include
    other sources like CTDOT Construction Advisories.
    """
    closures = fetch_ctroads_events(timeout=timeout)
    
    # Future: Add other sources here
    # closures.extend(fetch_ctdot_advisories())
    # closures.extend(fetch_city_closures())
    
    # Deduplicate and sort
    seen = set()
    unique_closures = []
    for closure in closures:
        key = (closure.get("road"), closure.get("start_time"))
        if key not in seen:
            seen.add(key)
            unique_closures.append(closure)
    
    return unique_closures[:10]  # Limit to 10 most relevant
