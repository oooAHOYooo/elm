import json
import os
import time
from typing import Any, Dict, List, Optional

import requests
from bs4 import BeautifulSoup  # type: ignore

URL = "https://www.newhavenct.gov/"
CACHE_FILE = os.path.join(os.path.dirname(__file__), "cache.json")
TTL = 1800  # 30 minutes

KEYWORDS = [
    "Health",
    "Pay",
    "Taxes",
    "Public Works",
    "Youth",
    "Recreation",
    "Jobs",
    "Affordable",
    "Housing",
    "Parks",
    "Report",
    "See, Click, Fix",
    "SeeClickFix",
    "Municity",
    "Permits",
    "City Plan",
    "Long Wharf",
    "Livable City",
    "Transportation",
    "Traffic",
    "Parking",
    "Recycling",
    "Board of Alders",
    "Arts",
    "Culture",
    "Tourism",
]


def load_cache() -> Optional[List[Dict[str, Any]]]:
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        if time.time() - data.get("timestamp", 0) > TTL:
            return None
        return data.get("payload")
    except Exception:
        return None


def save_cache(payload: List[Dict[str, Any]]) -> None:
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"timestamp": time.time(), "payload": payload}, f, indent=2)
    except Exception:
        # Best effort; ignore file I/O errors
        pass


def _normalize_url(href: str) -> str:
    href = (href or "").strip()
    if not href:
        return ""
    if href.startswith("http://") or href.startswith("https://"):
        return href
    if href.startswith("/"):
        return f"https://www.newhavenct.gov{href}"
    # relative path
    return f"https://www.newhavenct.gov/{href.lstrip('./')}"


def scrape() -> List[Dict[str, Any]]:
    """Scrape New Haven DOM and extract civic links."""
    html = requests.get(URL, timeout=12).text
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a", href=True)

    results: List[Dict[str, Any]] = []
    for a in links:
        text = (a.get_text() or "").strip()
        href = _normalize_url(a.get("href", ""))
        if not href or not text:
            continue
        for kw in KEYWORDS:
            if kw.lower() in text.lower():
                results.append({"title": text, "url": href, "category": kw})
                break

    # de-duplicate by URL while keeping first occurrence
    seen = set()
    final: List[Dict[str, Any]] = []
    for item in results:
        url = item.get("url")
        if not url or url in seen:
            continue
        seen.add(url)
        final.append(item)

    save_cache(final)
    return final


def get_live_data() -> List[Dict[str, Any]]:
    cached = load_cache()
    if cached:
        return cached
    return scrape()


