import logging
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import feedparser
import requests

_logger = logging.getLogger(__name__)

# Simple in-module cache
_CACHE: Dict[str, Any] = {
    "timestamp": 0.0,
    "data": [],
}


def _strip_html(html: str, max_len: int = 280) -> str:
    text = re.sub(r"<[^>]+>", "", html or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > max_len:
        return text[: max_len - 1].rstrip() + "…"
    return text


def _to_datetime(entry: Any) -> datetime:
    # Prefer published_parsed, then updated_parsed, else now
    for key in ("published_parsed", "updated_parsed"):
        ts = getattr(entry, key, None) or entry.get(key) if isinstance(entry, dict) else None
        if ts:
            try:
                return datetime.fromtimestamp(time.mktime(ts), tz=timezone.utc)
            except Exception:
                continue
    return datetime.now(tz=timezone.utc)


def _parse_entry(e: Any, source_title: str) -> Dict[str, Any]:
    published_dt = _to_datetime(e)
    summary = e.get("summary", "") or e.get("description", "") or ""
    image_url: Optional[str] = None

    # Try media content for images
    media_content = e.get("media_content") or e.get("media_thumbnail") or []
    if isinstance(media_content, list) and media_content:
        image_url = media_content[0].get("url")
    elif isinstance(media_content, dict):
        image_url = media_content.get("url")

    return {
        "title": e.get("title", "Untitled"),
        "link": e.get("link"),
        "published": published_dt,
        "published_display": published_dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "summary": _strip_html(summary),
        "source": source_title,
        "image": image_url,
        "category": "news",  # default category for RSS items
    }


def fetch_rss_feeds(
    feed_urls: List[str],
    per_feed_limit: int = 5,
    overall_limit: int = 20,
    request_timeout: int = 5,
) -> List[Dict[str, Any]]:
    """
    Fetch and aggregate items from multiple RSS feeds with basic caching.
    """
    now = time.time()
    # 5 minutes default cache TTL; callers can manage longer via upstream cache if needed
    ttl_seconds = 300
    if now - _CACHE["timestamp"] < ttl_seconds and _CACHE["data"]:
        return _CACHE["data"]

    all_items: List[Dict[str, Any]] = []
    headers = {
        "User-Agent": "ElmCityDaily/1.0 (+https://example.local)",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }

    for url in feed_urls:
        try:
            resp = requests.get(url, timeout=request_timeout, headers=headers)
            resp.raise_for_status()
            parsed = feedparser.parse(resp.content)
            source_title = parsed.feed.get("title", "Unknown Source")
            entries = parsed.entries[:per_feed_limit]
            for entry in entries:
                try:
                    item = _parse_entry(entry, source_title)
                    all_items.append(item)
                except Exception as parse_err:
                    _logger.warning("Failed to parse entry from %s: %s", source_title, parse_err)
        except Exception as err:
            _logger.error("Failed to fetch RSS feed %s: %s", url, err)
            continue

    # Sort by published desc
    all_items.sort(key=lambda x: x["published"], reverse=True)
    if overall_limit:
        all_items = all_items[:overall_limit]

    # Update cache
    _CACHE["timestamp"] = now
    _CACHE["data"] = all_items
    return all_items


