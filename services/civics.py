import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

_CACHE: Dict[str, Tuple[float, Any]] = {}
CITY_CAL_JSON = "https://cityofnewhaven.com/civicax/citycalendar/calendarjson"


def _get_cache(key: str, ttl: int) -> Optional[Any]:
    now = time.time()
    val = _CACHE.get(key)
    if not val:
        return None
    ts, data = val
    if now - ts > ttl:
        return None
    return data


def _set_cache(key: str, data: Any) -> None:
    _CACHE[key] = (time.time(), data)


def _get(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = 8) -> Any:
    headers = {"User-Agent": "ElmCityDaily/1.0 (+local)"}
    resp = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def fetch_recent_matters(
    city_slug: str = "newhaven",
    days_back: int = 120,
    limit: int = 250,
    ttl_seconds: int = 600,
) -> List[Dict[str, Any]]:
    """
    Fetch recent matters from the Legistar Web API for a given city.
    Normalizes to: title, status, date (ISO), date_display, type, file, link
    """
    cache_key = f"civics:matters:{city_slug}:{days_back}:{limit}"
    cached = _get_cache(cache_key, ttl_seconds)
    if cached is not None:
        return cached

    base = os.getenv("LEGISTAR_BASE", f"https://webapi.legistar.com/v1/{city_slug}")
    url = f"{base}/Matters"
    # Pull a chunk and filter locally; Legistar supports $top and $orderby widely
    params = {"$top": limit, "$orderby": "LastModifiedUtc desc"}
    try:
        data = _get(url, params=params)
    except Exception:
        _set_cache(cache_key, [])
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    normalized: List[Dict[str, Any]] = []
    for m in data or []:
        status = m.get("MatterStatusName") or ""
        title = m.get("MatterTitle") or m.get("MatterName") or ""
        file_no = m.get("MatterFile") or ""
        # Prefer passed/intro/last modified dates in that order
        dt = None
        for key in ("MatterPassedDate", "MatterIntroDate", "LastModifiedUtc"):
            raw = m.get(key)
            if not raw:
                continue
            try:
                # Legistar dates often in ISO with Z or /Date(x)/
                if isinstance(raw, str) and raw.endswith("Z"):
                    dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                elif isinstance(raw, str) and raw.startswith("/Date("):
                    # /Date(1690934400000)/
                    ms = int(raw[6:16])
                    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
                else:
                    # Fallback: try fromisoformat
                    dt = datetime.fromisoformat(str(raw))
            except Exception:
                dt = None
            if dt:
                break
        if not dt or dt < cutoff:
            continue

        matter_id = m.get("MatterId")
        # Best-effort link; may vary by municipality
        ui_host = os.getenv("LEGISTAR_UI_HOST", f"https://{city_slug}ct.legistar.com")
        link = f"{ui_host}/LegislationDetail.aspx?ID={matter_id}" if matter_id else ""

        normalized.append(
            {
                "title": title,
                "status": status,
                "type": m.get("MatterTypeName") or "",
                "file": file_no,
                "date_iso": dt.astimezone(timezone.utc).isoformat(),
                "date_display": dt.astimezone(timezone.utc).strftime("%Y-%m-%d"),
                "link": link,
            }
        )

    _set_cache(cache_key, normalized)
    return normalized


def compute_civics_stats(matters: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Derive simple stats from a list of normalized matters.
    """
    if not matters:
        return {
            "since": None,
            "introduced": 0,
            "adopted": 0,
            "failed": 0,
            "projects_open": 0,
        }
    dates = [m.get("date_iso") for m in matters if m.get("date_iso")]
    try:
        since = min(dates) if dates else None
    except Exception:
        since = None
    introduced = len(matters)
    adopted_names = {"Adopted", "Passed", "Approved"}
    failed_names = {"Rejected", "Failed", "Withdrawn"}
    adopted = sum(1 for m in matters if (m.get("status") or "") in adopted_names)
    failed = sum(1 for m in matters if (m.get("status") or "") in failed_names)
    # Heuristic: consider matters with type containing these keywords as "projects"
    project_keywords = ("Capital", "Project", "Development", "Construction")
    projects_open = sum(
        1
        for m in matters
        if any(k.lower() in (m.get("type") or "").lower() for k in project_keywords)
        and (m.get("status") or "") not in adopted_names | failed_names
    )
    return {
        "since": since,
        "introduced": introduced,
        "adopted": adopted,
        "failed": failed,
        "projects_open": projects_open,
    }


def fetch_tax_rate(
    municipality: str = "New Haven",
    ttl_seconds: int = 86_400,
) -> Optional[Dict[str, Any]]:
    """
    Fetch latest mill rate from a CT Open Data dataset.
    The dataset URL can be overridden via TAX_RATE_URL env var.
    Example (subject to change): https://data.ct.gov/resource/5cgs-jyrf.json?municipality=New%20Haven
    """
    cache_key = f"civics:tax:{municipality}"
    cached = _get_cache(cache_key, ttl_seconds)
    if cached is not None:
        return cached

    base_url = os.getenv("TAX_RATE_URL", "").strip()
    if not base_url:
        _set_cache(cache_key, None)
        return None
    try:
        data = _get(base_url, params={"municipality": municipality})
        if not data:
            _set_cache(cache_key, None)
            return None
        # Try to pick the most recent fiscal year
        latest = sorted(
            data,
            key=lambda r: (
                int(r.get("fiscal_year", 0))
                if str(r.get("fiscal_year", "0")).isdigit()
                else 0
            ),
            reverse=True,
        )[0]
        result = {
            "mill_rate": float(latest.get("mill_rate")) if latest.get("mill_rate") else None,
            "fiscal_year": latest.get("fiscal_year"),
            "source": base_url,
        }
        _set_cache(cache_key, result)
        return result
    except Exception:
        _set_cache(cache_key, None)
        return None

def fetch_city_calendar(limit: int = 8, ttl_seconds: int = 300) -> List[Dict[str, Any]]:
    """
    Fetch upcoming meetings/events from the city's Calendar JSON endpoint.
    Output keys: title, date_iso, date_display, link, location
    """
    cache_key = f"civics:calendar:{limit}"
    cached = _get_cache(cache_key, ttl_seconds)
    if cached is not None:
        return cached
    url = os.getenv("CITY_CALENDAR_JSON", CITY_CAL_JSON)
    try:
        data = _get(url)
    except Exception:
        _set_cache(cache_key, [])
        return []
    results: List[Dict[str, Any]] = []
    for ev in (data or [])[: limit * 2]:
        try:
            title = ev.get("Title") or ev.get("title") or ""
            when = ev.get("StartDate") or ev.get("start") or ev.get("Date")
            link = ev.get("Link") or ev.get("Url") or ev.get("url") or ""
            location = ev.get("Location") or ev.get("location") or ""
            # Normalize date
            dt = None
            if when:
                try:
                    # Try ISO first
                    if isinstance(when, str) and when.endswith("Z"):
                        from datetime import datetime, timezone
                        dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
                    else:
                        from dateutil import parser  # type: ignore
                        dt = parser.parse(str(when))
                except Exception:
                    dt = None
            if not dt:
                continue
            from datetime import timezone
            iso = dt.astimezone(timezone.utc).isoformat()
            disp = dt.strftime("%Y-%m-%d %I:%M %p")
            results.append(
                {"title": title, "date_iso": iso, "date_display": disp, "link": link, "location": location}
            )
        except Exception:
            continue
    # Sort ascending by date
    try:
        results.sort(key=lambda x: x.get("date_iso") or "")
    except Exception:
        pass
    results = results[:limit]
    _set_cache(cache_key, results)
    return results


def fetch_legistar_events(city_slug: str = "newhaven", limit: int = 8, ttl_seconds: int = 300) -> List[Dict[str, Any]]:
    """
    Fetch upcoming Legistar events (boards & commissions meetings).
    Output keys: title, date_iso, date_display, body, link, location
    """
    cache_key = f"civics:legistar_events:{city_slug}:{limit}"
    cached = _get_cache(cache_key, ttl_seconds)
    if cached is not None:
        return cached
    base = os.getenv("LEGISTAR_BASE", f"https://webapi.legistar.com/v1/{city_slug}")
    url = f"{base}/events"
    params = {"$top": limit, "$orderby": "EventDate asc"}
    try:
        data = _get(url, params=params)
    except Exception:
        _set_cache(cache_key, [])
        return []
    results: List[Dict[str, Any]] = []
    for ev in (data or [])[: limit * 2]:
        try:
            title = ev.get("EventComment") or ev.get("EventBodyName") or "Meeting"
            body = ev.get("EventBodyName") or ""
            when = ev.get("EventDate")
            location = ev.get("EventLocation") or ""
            event_id = ev.get("EventId")
            ui_host = os.getenv("LEGISTAR_UI_HOST", f"https://{city_slug}ct.legistar.com")
            link = f"{ui_host}/MeetingDetail.aspx?ID={event_id}" if event_id else ""
            dt = None
            if when:
                try:
                    if isinstance(when, str) and when.endswith("Z"):
                        from datetime import datetime, timezone
                        dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
                    elif isinstance(when, str) and when.startswith("/Date("):
                        ms = int(when[6:19])
                        from datetime import datetime, timezone
                        dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
                    else:
                        from dateutil import parser  # type: ignore
                        dt = parser.parse(str(when))
                except Exception:
                    dt = None
            if not dt:
                continue
            from datetime import timezone
            iso = dt.astimezone(timezone.utc).isoformat()
            disp = dt.strftime("%Y-%m-%d %I:%M %p")
            results.append(
                {"title": title, "date_iso": iso, "date_display": disp, "body": body, "link": link, "location": location}
            )
        except Exception:
            continue
    try:
        results.sort(key=lambda x: x.get("date_iso") or "")
    except Exception:
        pass
    results = results[:limit]
    _set_cache(cache_key, results)
    return results


