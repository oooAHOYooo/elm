from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup
from utils.cache import TTLCache


_TIME_RE = re.compile(r"^(\d{1,2}):(\d{2})\s*([ap])\.m\.\s*$", re.IGNORECASE)
_DATE_RE = re.compile(r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+([A-Za-z]{3,})\s+(\d{1,2}),\s+(\d{4})\s*$")

_MONTHS = {
    "Jan": 1, "January": 1,
    "Feb": 2, "February": 2,
    "Mar": 3, "March": 3,
    "Apr": 4, "April": 4,
    "May": 5,
    "Jun": 6, "June": 6,
    "Jul": 7, "July": 7,
    "Aug": 8, "August": 8,
    "Sep": 9, "Sept": 9, "September": 9,
    "Oct": 10, "October": 10,
    "Nov": 11, "November": 11,
    "Dec": 12, "December": 12,
}


def _parse_time_component(s: str) -> Optional[Dict[str, int]]:
    m = _TIME_RE.match(s.strip())
    if not m:
        return None
    hour = int(m.group(1))
    minute = int(m.group(2))
    ap = m.group(3).lower()
    if ap == "a":
        # 12:xx a.m. -> 00:xx
        hour = 0 if hour == 12 else hour
    else:
        # 12:xx p.m. -> 12:xx; otherwise add 12
        hour = 12 if hour == 12 else hour + 12
    return {"hour": hour, "minute": minute}


def _parse_date_heading(s: str) -> Optional[datetime]:
    m = _DATE_RE.match(s.strip())
    if not m:
        return None
    # weekday = m.group(1)  # not used
    mon_name = m.group(2)
    day = int(m.group(3))
    year = int(m.group(4))
    month = _MONTHS.get(mon_name, None)
    if not month:
        return None
    try:
        return datetime(year, month, day)
    except Exception:
        return None


def _read_source_lines() -> List[str]:
    src_path = Path(__file__).with_name("newhavenlist.txt")
    try:
        return src_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []

def _fetch_lines_from_web(url: str, request_timeout: int = 8) -> List[str]:
    try:
        headers = {
            "User-Agent": "ElmCityDaily/1.0 (+https://example.local)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        resp = requests.get(url, timeout=request_timeout, headers=headers)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # Extract visible text and normalize
        text = soup.get_text("\n")
        # Remove superfluous blank lines
        lines = [ln.rstrip() for ln in text.splitlines()]
        # Strip leading/trailing global empties but retain structure-ish breaks
        return lines
    except Exception:
        return []

_cache = TTLCache(ttl_seconds=30 * 60, filepath=".cache_nhl.pkl")  # 30 minutes


def _make_gcal_link(title: str, start: datetime, end: Optional[datetime], location: str) -> str:
    """Generate a Google Calendar event link."""
    # Dates must be YYYYMMDDTHHMMSSZ
    fmt = "%Y%m%dT%H%M%S"
    # Assuming start is aware; convert to UTC
    t_start = start.astimezone(ZoneInfo("UTC")).strftime(fmt) + "Z"
    if end:
        t_end = end.astimezone(ZoneInfo("UTC")).strftime(fmt) + "Z"
    else:
        # Default to 1 hour
        from datetime import timedelta
        t_end = (start + timedelta(hours=1)).astimezone(ZoneInfo("UTC")).strftime(fmt) + "Z"
    
    import urllib.parse
    base = "https://www.google.com/calendar/render?action=TEMPLATE"
    params = {
        "text": title,
        "dates": f"{t_start}/{t_end}",
        "location": location,
        "sf": "true",
        "output": "xml"
    }
    return base + "&" + urllib.parse.urlencode(params)


def load_events(tz: ZoneInfo) -> List[Dict[str, Any]]:
    """
    Parse The New Haven List events into structured event dicts for the homepage.
    Attempts live fetch; falls back to bundled text if unavailable.
    Returns items with keys: title, location, date_iso, source, summary, link, published_display.
    """
    # Try cache first
    cached = _cache.get("nhl_events_lines")
    if cached is not None:
        lines = cached
    else:
        # Try web first
        lines = _fetch_lines_from_web("https://newhavenlist.com")
        if not lines:
            lines = _read_source_lines()
        _cache.set("nhl_events_lines", lines)

    if not lines:
        return []

    events: List[Dict[str, Any]] = []
    current_date: Optional[datetime] = None  # naive date; time added per event
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i].strip()
        # Update current date when we hit a date heading
        dt_heading = _parse_date_heading(line)
        if dt_heading:
            current_date = dt_heading
            i += 1
            continue

        # Skip boilerplate rows
        if not line or line.lower().startswith("times") or line.lower() == "+ google" or line == "—":
            i += 1
            continue

        # Look for a start time
        t_start = _parse_time_component(line)
        if not t_start:
            i += 1
            continue

        # We have a start time; see if next line is "-end time"
        t_end: Optional[Dict[str, int]] = None
        title_line_idx = i + 1
        if title_line_idx < n:
            next_line = lines[title_line_idx].strip()
            if next_line.startswith("-"):
                t_end = _parse_time_component(next_line[1:].strip())
                title_line_idx += 1

        # Title and location
        if title_line_idx + 2 < n:
            title = lines[title_line_idx].strip()
            location = lines[title_line_idx + 1].strip()
            # Following line likely "+ Google", but tolerate if absent
        else:
            # Not enough lines; abort this block
            i += 1
            continue

        # Build datetime(s)
        if not current_date:
            # Without a current date, we cannot build a full datetime
            i = title_line_idx + 1
            continue

        try:
            dt_local_start = datetime(
                current_date.year, current_date.month, current_date.day,
                t_start["hour"], t_start["minute"], 0, 0, tzinfo=tz
            )
        except Exception:
            i = title_line_idx + 1
            continue

        dt_local_end: Optional[datetime] = None
        if t_end:
            try:
                dt_local_end = datetime(
                    current_date.year, current_date.month, current_date.day,
                    t_end["hour"], t_end["minute"], 0, 0, tzinfo=tz
                )
            except Exception:
                dt_local_end = None

        # Normalize to expected fields
        gcal_link = _make_gcal_link(title, dt_local_start, dt_local_end, location)
        events.append(
            {
                "title": title,
                "location": location,
                "date_iso": dt_local_start.astimezone(ZoneInfo("UTC")).isoformat(),
                "source": {"name": "The New Haven List", "url": "https://newhavenlist.com"},
                "summary": "",
                "link": gcal_link,  # Use Google Calendar link as the main link
                "published_display": dt_local_start.strftime("%Y-%m-%d %I:%M %p"),
                # Keep end for potential future use
                "end_iso": dt_local_end.astimezone(ZoneInfo("UTC")).isoformat() if dt_local_end else None,
            }
        )

        # Advance i to after "+ Google" if present; otherwise to next after location
        # Typically: title_line_idx -> title, +1 -> location, +2 -> "+ Google"
        i = title_line_idx + 3

    return events


