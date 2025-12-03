"""
Traffic Camera Service for Elm City Daily

Provides access to CT DOT and other public traffic camera feeds.
Note: CT DOT cameras do not record. No recordings are available for disclosure.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

_logger = logging.getLogger(__name__)

# CT DOT Traffic Camera Configuration
# These are example camera configurations for New Haven area
# Actual URLs may need to be discovered by inspecting ctroads.org
TRAFFIC_CAMS = [
    {
        "id": "i95_qbridge_nb",
        "label": "I-95 Q Bridge NB – New Haven",
        "highway": "I-95",
        "direction": "Northbound",
        "location": "Q Bridge",
        "thumbnail_url": "https://ctroads.org/cameras/i95_qbridge_nb.jpg",
        "feed_url": "https://ctroads.org/cameras/i95_qbridge_nb.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i91_trumbull_st",
        "label": "I-91 @ Trumbull St – New Haven",
        "highway": "I-91",
        "direction": "Northbound",
        "location": "Trumbull Street",
        "thumbnail_url": "https://ctroads.org/cameras/i91_trumbull.jpg",
        "feed_url": "https://ctroads.org/cameras/i91_trumbull.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i95_exit48",
        "label": "I-95 Exit 48 – New Haven",
        "highway": "I-95",
        "direction": "Southbound",
        "location": "Exit 48",
        "thumbnail_url": "https://ctroads.org/cameras/i95_exit48.jpg",
        "feed_url": "https://ctroads.org/cameras/i95_exit48.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i84_exit25",
        "label": "I-84 Exit 25 – Hartford Area",
        "highway": "I-84",
        "direction": "Eastbound",
        "location": "Exit 25",
        "thumbnail_url": "https://ctroads.org/cameras/i84_exit25.jpg",
        "feed_url": "https://ctroads.org/cameras/i84_exit25.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "route2_middletown",
        "label": "Route 2 – Middletown",
        "highway": "Route 2",
        "direction": "Eastbound",
        "location": "Middletown",
        "thumbnail_url": "https://ctroads.org/cameras/route2_middletown.jpg",
        "feed_url": "https://ctroads.org/cameras/route2_middletown.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "route8_waterbury",
        "label": "Route 8 – Waterbury",
        "highway": "Route 8",
        "direction": "Northbound",
        "location": "Waterbury",
        "thumbnail_url": "https://ctroads.org/cameras/route8_waterbury.jpg",
        "feed_url": "https://ctroads.org/cameras/route8_waterbury.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i91_exit1",
        "label": "I-91 Exit 1 – New Haven",
        "highway": "I-91",
        "direction": "Southbound",
        "location": "Exit 1",
        "thumbnail_url": "https://ctroads.org/cameras/i91_exit1.jpg",
        "feed_url": "https://ctroads.org/cameras/i91_exit1.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i95_exit47",
        "label": "I-95 Exit 47 – New Haven",
        "highway": "I-95",
        "direction": "Northbound",
        "location": "Exit 47",
        "thumbnail_url": "https://ctroads.org/cameras/i95_exit47.jpg",
        "feed_url": "https://ctroads.org/cameras/i95_exit47.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i91_exit8",
        "label": "I-91 Exit 8 – New Haven",
        "highway": "I-91",
        "direction": "Northbound",
        "location": "Exit 8",
        "thumbnail_url": "https://ctroads.org/cameras/i91_exit8.jpg",
        "feed_url": "https://ctroads.org/cameras/i91_exit8.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i95_exit46",
        "label": "I-95 Exit 46 – New Haven",
        "highway": "I-95",
        "direction": "Southbound",
        "location": "Exit 46",
        "thumbnail_url": "https://ctroads.org/cameras/i95_exit46.jpg",
        "feed_url": "https://ctroads.org/cameras/i95_exit46.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "i84_exit39",
        "label": "I-84 Exit 39 – Hartford",
        "highway": "I-84",
        "direction": "Westbound",
        "location": "Exit 39",
        "thumbnail_url": "https://ctroads.org/cameras/i84_exit39.jpg",
        "feed_url": "https://ctroads.org/cameras/i84_exit39.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
    {
        "id": "route9_old_lyme",
        "label": "Route 9 – Old Lyme",
        "highway": "Route 9",
        "direction": "Northbound",
        "location": "Old Lyme",
        "thumbnail_url": "https://ctroads.org/cameras/route9_oldlyme.jpg",
        "feed_url": "https://ctroads.org/cameras/route9_oldlyme.jpg",
        "refresh_ms": 5000,
        "source": "CT DOT",
        "source_url": "https://ctroads.org",
    },
]


def get_all_cameras() -> List[Dict[str, Any]]:
    """
    Returns list of all available traffic cameras.
    Each camera dict includes: id, label, highway, direction, location,
    thumbnail_url, feed_url, refresh_ms, source, source_url
    """
    return TRAFFIC_CAMS.copy()


def get_camera_by_id(camera_id: str) -> Optional[Dict[str, Any]]:
    """
    Returns a specific camera by ID, or None if not found.
    """
    for cam in TRAFFIC_CAMS:
        if cam["id"] == camera_id:
            return cam.copy()
    return None


def get_cameras_by_highway(highway: str) -> List[Dict[str, Any]]:
    """
    Returns cameras filtered by highway (e.g., "I-95", "I-91", "Route 2").
    """
    return [cam.copy() for cam in TRAFFIC_CAMS if cam.get("highway") == highway]


def get_cameras_by_location(location_keyword: str) -> List[Dict[str, Any]]:
    """
    Returns cameras filtered by location keyword (case-insensitive).
    """
    keyword_lower = location_keyword.lower()
    return [
        cam.copy()
        for cam in TRAFFIC_CAMS
        if keyword_lower in cam.get("location", "").lower()
        or keyword_lower in cam.get("label", "").lower()
    ]


def get_camera_metadata() -> Dict[str, Any]:
    """
    Returns metadata about the camera system.
    """
    return {
        "total_cameras": len(TRAFFIC_CAMS),
        "sources": list(set(cam.get("source", "Unknown") for cam in TRAFFIC_CAMS)),
        "highways": sorted(list(set(cam.get("highway", "") for cam in TRAFFIC_CAMS))),
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "attribution": {
            "ct_dot": {
                "name": "CT DOT",
                "url": "https://ctroads.org",
                "note": "CT DOT traffic cameras are for live monitoring only. No recordings are available for disclosure.",
            }
        },
    }

