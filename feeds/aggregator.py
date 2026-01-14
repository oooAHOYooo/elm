import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Any, Dict, List, Optional

from .feed_parser import parse_rss, parse_ical
from .iaff_scraper import fetch_iaff_headlines
from .newhavenlist import load_events
from .sources import RSS_SOURCES, ICAL_SOURCES, SOURCE_CREDIT
from utils.cache import TTLCache

_logger = logging.getLogger(__name__)
_cache = TTLCache(ttl_seconds=600, filepath=".cache_feeds.pkl")
# Thread pool for parallel RSS feed fetching
_feed_executor = ThreadPoolExecutor(max_workers=6)


def _sort_key(item: Dict[str, Any]) -> float:
    try:
        if item.get("date"):
            return datetime.fromisoformat(item["date"].replace("Z", "+00:00")).timestamp()
    except Exception:
        pass
    return 0.0


def aggregate_all(timeout_rss: int = 5, timeout_ical: int = 6) -> Dict[str, Any]:  # Reduced timeouts for 10% speedup
    cached = _cache.get("feeds:all")
    if cached:
        return cached

    items: List[Dict[str, Any]] = []

    # Parallel RSS feed fetching for better performance
    rss_futures = {}
    for name, url in RSS_SOURCES.items():
        if name == "iaff_headlines":
            continue  # Handle separately below
        rss_futures[_feed_executor.submit(parse_rss, url, timeout_rss, name)] = name

    # Fetch RSS feeds in parallel
    for future in as_completed(rss_futures, timeout=timeout_rss * 2):
        try:
            feed_items = future.result()
            items.extend(feed_items)
        except Exception as e:
            name = rss_futures[future]
            _logger.warning(f"Failed to fetch RSS feed {name}: {e}")

    # iCal sources (usually empty, but handle if present)
    for name, url in ICAL_SOURCES.items():
        try:
            items.extend(parse_ical(url, timeout=timeout_ical))
        except Exception as e:
            _logger.warning(f"Failed to fetch iCal {name}: {e}")

    # The New Haven List (local events) - fast, local file
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

    # IAFF Headlines special scraper (can be slow, run separately)
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


