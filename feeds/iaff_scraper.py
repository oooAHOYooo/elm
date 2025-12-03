import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List, Dict, Any

from .sources import SOURCE_META

_logger = logging.getLogger(__name__)


def fetch_iaff_headlines(url: str) -> List[Dict[str, Any]]:
    """
    Scrapes IAFF Headlines page and converts result into Elm City Daily feed items.
    Returns items in the same format as normalize_item from feed_parser.py
    """
    headers = {
        "User-Agent": "ElmCityDaily/1.0 (+https://elm-city-daily.local)"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=8)
        resp.raise_for_status()
    except Exception as e:
        _logger.error("Failed to fetch IAFF headlines from %s: %s", url, e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    # IAFF headline items are typically in div.newsItem or table rows
    # If structure changes, this selector still captures primary items.
    items = soup.select("td, div, li")
    headlines = []

    for el in items:
        link_el = el.find("a")
        if not link_el:
            continue
        
        title = link_el.get_text(strip=True)
        if not title:
            continue

        link = link_el.get("href", "")
        if link and not link.startswith("http"):
            link = "https://newhavenfire.org" + link
        elif not link:
            link = url

        # Use current time as published date since page doesn't provide dates
        published_dt = datetime.now(timezone.utc)
        date_iso = published_dt.isoformat()

        # Get source meta
        source_key = "iaff_headlines"
        meta = SOURCE_META.get(source_key, {"name": "IAFF Local 825", "url": "https://newhavenfire.org"})

        # Create credit similar to normalize_item format
        credit = {
            "source": meta["name"],
            "url": meta["url"],
            "note": "Data scraped from public IAFF firefighter news headlines.",
        }

        # Format item to match normalize_item output
        item: Dict[str, Any] = {
            "title": title,
            "link": link,
            "summary": title,  # Use title as summary since no description available
            "date": date_iso,
            "location": "",
            "category": "fire",
            "source": meta,
            "credit": credit,
            "source_name": "IAFF Local 825",
            "feed_type": "scraped",
        }

        headlines.append(item)

    return headlines

