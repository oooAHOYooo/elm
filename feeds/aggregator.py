import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .feed_parser import parse_rss, parse_ical
from .iaff_scraper import fetch_iaff_headlines
from .newhavenlist import load_events
from .sources import RSS_SOURCES, ICAL_SOURCES, SOURCE_CREDIT
from utils.cache import TTLCache

_logger = logging.getLogger(__name__)
_cache = TTLCache(ttl_seconds=600, filepath=".cache_feeds.pkl")


def _sort_key(item: Dict[str, Any]) -> float:
    try:
        if item.get("date"):
            return datetime.fromisoformat(item["date"].replace("Z", "+00:00")).timestamp()
    except Exception:
        pass
    return 0.0


def aggregate_all(timeout_rss: int = 6, timeout_ical: int = 8) -> Dict[str, Any]:
    cached = _cache.get("feeds:all")
    if cached:
        return cached

    items: List[Dict[str, Any]] = []

    # RSS sources (skip iaff_headlines as it's not an RSS feed)
    for name, url in RSS_SOURCES.items():
        if name == "iaff_headlines":
            continue  # Handle separately below
        items.extend(parse_rss(url, timeout=timeout_rss, source_key=name))

    # iCal sources
    for name, url in ICAL_SOURCES.items():
        items.extend(parse_ical(url, timeout=timeout_ical))

    # The New Haven List (local events)
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("America/New_York")
        nhl_events = load_events(tz=tz)
        # Normalize category
        for ev in nhl_events:
            ev["category"] = "events"
        items.extend(nhl_events)
    except Exception as e:
        _logger.error("New Haven List error: %s", e)

    # IAFF Headlines special scraper
    if "iaff_headlines" in RSS_SOURCES:
        try:
            iaff_items = fetch_iaff_headlines(RSS_SOURCES["iaff_headlines"])
            items.extend(iaff_items)
        except Exception as e:
            _logger.error("IAFF scraper error: %s", e)

    # Sort newest first
    items.sort(key=_sort_key, reverse=True)

    result = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "source_credit": SOURCE_CREDIT,
        "items": items,
    }

    _cache.set("feeds:all", result)
    return result


def aggregate_filtered(category: Optional[str] = None) -> Dict[str, Any]:
    data = aggregate_all()
    if not category:
        return data
    filtered = [i for i in data["items"] if (i.get("category") == category)]
    return {
        "updated": data["updated"],
        "source_credit": data["source_credit"],
        "items": filtered,
    }


