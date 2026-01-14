import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser
import requests
from ics import Calendar

from .sources import SOURCE_CREDIT, SOURCE_META

_logger = logging.getLogger(__name__)


def parse_rss(url: str, timeout: int = 6, source_key: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
    """Parse RSS feed with optional limit for performance"""
    try:
        headers = {
            "User-Agent": "ElmCityDaily/1.0 (+https://example.local)",
            "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
        }
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        parsed = feedparser.parse(resp.content)
        items: List[Dict[str, Any]] = []
        # Limit entries early for performance
        entries = parsed.entries[:limit] if limit else parsed.entries
        for e in entries:
            items.append(
                normalize_item(
                    raw=e,
                    feed_type="rss",
                    source_name=parsed.feed.get("title", "InfoNewHaven"),
                    source_key=source_key,
                )
            )
        return items
    except Exception as err:
        _logger.error("parse_rss failed for %s: %s", url, err)
        return []


def parse_ical(url: str, timeout: int = 8) -> List[Dict[str, Any]]:
    try:
        headers = {"User-Agent": "ElmCityDaily/1.0 (+https://example.local)"}
        resp = requests.get(url, timeout=timeout, headers=headers)
        resp.raise_for_status()
        cal = Calendar(resp.text)
        items: List[Dict[str, Any]] = []
        for event in cal.events:
            items.append(
                normalize_item(
                    raw=event,
                    feed_type="ical",
                    source_name="InfoNewHaven Events",
                )
            )
        return items
    except Exception as err:
        _logger.error("parse_ical failed for %s: %s", url, err)
        return []


def _coerce_dt(dt: Any) -> Optional[str]:
    try:
        if hasattr(dt, "astimezone"):
            # ics returns arrow date/time; convert to aware ISO
            return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    try:
        # RSS datetime in struct_time or datetime
        if isinstance(dt, datetime):
            d = dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
            return d.astimezone(timezone.utc).isoformat()
    except Exception:
        pass
    return None


def normalize_item(raw: Any, feed_type: str, source_name: str, source_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Normalize items across RSS and iCal feeds.
    Output keys: title, summary, link, date, category, source, credit
    """
    if feed_type == "rss":
        title = getattr(raw, "title", None) or raw.get("title", "")
        link = getattr(raw, "link", None) or raw.get("link", "")
        summary = getattr(raw, "summary", None) or raw.get("description", "") or ""
        location = getattr(raw, "location", None) or raw.get("location", "")

        # date handling
        published = getattr(raw, "published_parsed", None) or raw.get("published_parsed")
        updated = getattr(raw, "updated_parsed", None) or raw.get("updated_parsed")
        dt = None
        if published:
            try:
                dt = datetime(*published[:6], tzinfo=timezone.utc)
            except Exception:
                dt = None
        if not dt and updated:
            try:
                dt = datetime(*updated[:6], tzinfo=timezone.utc)
            except Exception:
                dt = None

        # Map category based on known source keys
        if source_key == "who_knew":
            category = "who_knew_blog"
        elif source_key == "food_drink":
            category = "food_drink"
        elif source_key == "music_arts":
            category = "music_arts"
        elif source_key == "city_news":
            category = "city_news"
        elif source_key == "city_events":
            category = "city_events"
        elif source_key == "city_calendar_items":
            category = "city_calendar_items"
        else:
            category = "news"

    elif feed_type == "ical":
        title = getattr(raw, "name", None) or ""
        link = getattr(raw, "url", None) or ""
        summary = getattr(raw, "description", None) or ""
        # ics Event often provides location
        location = getattr(raw, "location", None) or ""
        # ics Event has begin/end
        dt = None
        try:
            if getattr(raw, "begin", None):
                dt = raw.begin.datetime
        except Exception:
            dt = None
        category = "events"
    else:
        title = ""
        link = ""
        summary = ""
        location = ""
        dt = None
        category = "news"

    date_iso = _coerce_dt(dt) if dt else None

    # Source meta (default to InfoNewHaven for backwards compatibility)
    meta = SOURCE_META.get(source_key or "", {"name": "InfoNewHaven.com", "url": "https://www.infonewhaven.com"})

    # Credit: use InfoNewHaven note only for InfoNewHaven items; otherwise basic credit
    if meta["name"] == "InfoNewHaven.com":
        credit = {
            "source": "InfoNewHaven.com",
            "url": "https://www.infonewhaven.com",
            "note": "All RSS/iCal feeds are provided courtesy of InfoNewHaven.com — Visit | Stay | Play | Live Here in the Elm City.",
        }
    else:
        credit = {
            "source": meta["name"],
            "url": meta["url"],
        }

    item: Dict[str, Any] = {
        "title": title or "",
        "link": link or "",
        "summary": summary or "",
        "date": date_iso,
        "location": location or "",
        "category": category,
        "source": meta,
        "credit": credit,
        "source_name": source_name,
        "feed_type": feed_type,
    }
    return item


