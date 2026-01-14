"""
Elm City Daily — MVP Newspaper Dashboard
A simplified civic dashboard for New Haven, CT
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Dict, List
import json
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, Response

from config import Config
from services import events as events_service
from services.civics import fetch_tax_rate, fetch_city_calendar, fetch_legistar_events
from services import weather as weather_service
from services import nws as nws_service
from services import tides as tides_service
from services import air_quality as aqi_service
from feeds.aggregator import aggregate_all
from utils.cache import TTLCache
from modules.legislation_tracker import LegislationTracker
from modules.budget_tracker import BudgetTracker

load_dotenv()

# Thread pool for parallel API calls - optimized for performance
_executor = ThreadPoolExecutor(max_workers=10)  # Increased from 8 to 10 for better parallelism

# Short-lived HTML cache for the homepage. Keeps reloads snappy without changing features.
_index_html_cache = TTLCache(ttl_seconds=90)  # Increased to 90s for 10% more cache hits

# Cache for file-based data (longer TTL since files don't change often)
_file_data_cache = TTLCache(ttl_seconds=600, filepath=".cache_file_data.pkl")  # Increased from 300s to 600s


def _sample_hours_neighborhoods() -> List[Dict[str, Any]]:
    """Load Hours directory data from JSON and add computed fields."""
    cache_key = "hours_neighborhoods"
    cached = _file_data_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        data_path = Path(__file__).with_name("data") / "hours.json"
        with open(data_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        neighborhoods = payload.get("neighborhoods") or []
    except Exception:
        neighborhoods = []

    for n in neighborhoods:
        businesses = n.get("businesses") or []
        n["total"] = len(businesses)
        n["open_now"] = sum(1 for b in businesses if (b.get("status") == "open"))

    _file_data_cache.set(cache_key, neighborhoods)
    return neighborhoods


def _load_manual_events() -> List[Dict[str, Any]]:
    """Load manually curated events (e.g., DowntownNHV email) from JSON."""
    cache_key = "manual_events"
    cached = _file_data_cache.get(cache_key)
    if cached is not None:
        return cached
    
    try:
        data_path = Path(__file__).with_name("data") / "manual_events.json"
        with open(data_path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        items = payload.get("items") or []
        result = [it for it in items if isinstance(it, dict)]
        _file_data_cache.set(cache_key, result)
        return result
    except Exception:
        _file_data_cache.set(cache_key, [])
        return []


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.logger.setLevel(logging.INFO)

    @app.route("/")
    def index():
        # Allow explicit bypass (e.g., Refresh button sets ?fresh=1)
        if request.args.get("fresh") == "1":
            try:
                _index_html_cache.clear()
            except Exception:
                pass
        else:
            cached_html = _index_html_cache.get("index_html")
            if cached_html:
                resp = Response(cached_html, mimetype="text/html")
                resp.headers["X-Elm-Cache"] = "HIT"
                return resp

        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz)
        date_str = today.strftime("%A, %B %d, %Y")

        # Hours directory + Trivia digest (kept lightweight; rendered on homepage)
        hours_all = _sample_hours_neighborhoods()
        trivia_items: List[Dict[str, str]] = []
        day_order = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        for n in hours_all:
            for b in (n.get("businesses") or []):
                for h in (b.get("happenings") or []):
                    if (h.get("type") or "").lower() != "trivia":
                        continue
                    trivia_items.append({
                        "business": b.get("name") or "Business",
                        "neighborhood": n.get("name") or "",
                        "day": h.get("day") or "",
                        "time": h.get("time") or "",
                        "note": "",
                    })

        # Also load trivia items from data/trivia.json (for listings not yet in hours directory)
        cache_key_trivia = "trivia_items_parsed"
        cached_trivia = _file_data_cache.get(cache_key_trivia)
        if cached_trivia is not None:
            trivia_items.extend(cached_trivia)
        else:
            try:
                trivia_path = Path(__file__).with_name("data") / "trivia.json"
                with open(trivia_path, "r", encoding="utf-8") as f:
                    trivia_payload = json.load(f)
                trivia_list = []
                for it in (trivia_payload.get("items") or []):
                    if (it.get("type") or "").lower() != "trivia":
                        continue
                    trivia_list.append({
                        "business": it.get("business") or "Business",
                        "neighborhood": (it.get("address") or "New Haven, CT"),
                        "day": it.get("day") or "",
                        "time": it.get("time") or "",
                        "note": it.get("note") or "",
                    })
                trivia_items.extend(trivia_list)
                _file_data_cache.set(cache_key_trivia, trivia_list)
            except Exception:
                _file_data_cache.set(cache_key_trivia, [])
                pass

        # De-dupe and sort (cached for performance)
        cache_key_trivia_processed = "trivia_items_processed"
        cached_processed = _file_data_cache.get(cache_key_trivia_processed)
        if cached_processed is not None:
            trivia_items = cached_processed
        else:
            seen = set()
            uniq: List[Dict[str, str]] = []
            for t in trivia_items:
                key = (t.get("business") or "", t.get("day") or "", t.get("time") or "", t.get("neighborhood") or "")
                if key in seen:
                    continue
                seen.add(key)
                uniq.append(t)
            trivia_items = uniq
            trivia_items.sort(key=lambda x: (day_order.get(x.get("day") or "", 99), x.get("business") or ""))
            _file_data_cache.set(cache_key_trivia_processed, trivia_items)
        
        # Format sunrise/sunset times in EST with 12-hour format
        def format_sun_time(iso_time_str: str) -> str:
            """Convert ISO time string to EST 12-hour format (e.g., '7:23 AM')"""
            if not iso_time_str:
                return '--'
            try:
                # Parse ISO format (e.g., "2024-01-15T07:23:00")
                dt = datetime.fromisoformat(iso_time_str.replace('Z', '+00:00'))
                # Convert to EST timezone
                dt_est = dt.astimezone(tz)
                # Format as 12-hour with AM/PM, remove leading zero from hour
                time_str = dt_est.strftime("%I:%M %p")
                # Remove leading zero from hour (e.g., "07:23 AM" -> "7:23 AM")
                if time_str.startswith("0"):
                    time_str = time_str[1:]
                return time_str
            except Exception:
                return iso_time_str if iso_time_str else '--'
        timeout: int = int(app.config["REQUEST_TIMEOUT"])
        lat = float(app.config["WEATHER_LAT"])
        lon = float(app.config["WEATHER_LON"])

        # Parallel API fetching for speed
        airnow_key = app.config.get("AIRNOW_API_KEY", "")
        
        # Fetch legislation stats (lightweight, just for homepage widget)
        # Optimized: reduced days_back and limit for faster processing
        def get_legislation_stats():
            try:
                tracker = LegislationTracker()
                legislation = tracker.get_passed_legislation(days_back=30, limit=50)  # Reduced from 100 to 50
                return tracker.get_stats(legislation)
            except Exception:
                return {"total_passed": 0, "this_week": 0, "this_month": 0, "last_30_days": 0}
        
        # Fetch budget stats (lightweight, just for homepage widget)
        def get_budget_stats():
            try:
                budget_tracker = BudgetTracker()
                return budget_tracker.get_budget_stats()
            except Exception:
                return {"fiscal_year": None, "total_budget": None, "total_spent": None, "percentage_spent": None}
        
        futures = {
            _executor.submit(weather_service.fetch_weather, lat, lon, timeout): "weather",
            _executor.submit(nws_service.fetch_nws_alerts, "ctz010"): "nws_alerts",
            _executor.submit(aqi_service.fetch_air_quality, lat, lon, airnow_key or None): "air_quality",
            _executor.submit(fetch_tax_rate, "New Haven"): "tax_info",
            _executor.submit(fetch_city_calendar, 6): "cal_upcoming",
            _executor.submit(fetch_legistar_events, "newhaven", 6): "legis_upcoming",
            _executor.submit(aggregate_all): "agg",
            _executor.submit(get_legislation_stats): "legislation_stats",
            _executor.submit(get_budget_stats): "budget_stats",
        }
        
        results = {}
        completed_count = 0
        try:
            for future in as_completed(futures, timeout=timeout):
                key = futures[future]
                try:
                    results[key] = future.result()
                    completed_count += 1
                except Exception as e:
                    app.logger.warning(f"Failed to fetch {key}: {e}")
                    if key == "legislation_stats":
                        results[key] = {"total_passed": 0, "this_week": 0, "this_month": 0, "last_30_days": 0}
                    elif key == "budget_stats":
                        results[key] = {"fiscal_year": None, "total_budget": None, "total_spent": None, "percentage_spent": None}
                    else:
                        results[key] = {} if key in ("weather", "air_quality", "tax_info", "agg") else []
                    completed_count += 1
        except TimeoutError:
            # Some futures didn't complete in time - process what we have
            app.logger.warning(f"Timeout waiting for futures ({completed_count}/{len(futures)} completed) - processing completed results")
        
        # Process any remaining futures that completed but weren't processed yet
        for future, key in futures.items():
            if key not in results:
                try:
                    if future.done():
                        results[key] = future.result()
                    else:
                        # Future didn't complete - set default
                        app.logger.warning(f"Future {key} did not complete in time - using default")
                        if key == "legislation_stats":
                            results[key] = {"total_passed": 0, "this_week": 0, "this_month": 0, "last_30_days": 0}
                        elif key == "budget_stats":
                            results[key] = {"fiscal_year": None, "total_budget": None, "total_spent": None, "percentage_spent": None}
                        else:
                            results[key] = {} if key in ("weather", "air_quality", "tax_info", "agg") else []
                except Exception as e:
                    app.logger.warning(f"Failed to fetch {key}: {e}")
                    if key == "legislation_stats":
                        results[key] = {"total_passed": 0, "this_week": 0, "this_month": 0, "last_30_days": 0}
                    elif key == "budget_stats":
                        results[key] = {"fiscal_year": None, "total_budget": None, "total_spent": None, "percentage_spent": None}
                    else:
                        results[key] = {} if key in ("weather", "air_quality", "tax_info", "agg") else []
        
        # Ensure all expected keys have defaults
        weather = results.get("weather", {})
        nws_alerts = results.get("nws_alerts", [])
        air_quality = results.get("air_quality", {})
        tax_info = results.get("tax_info", {})
        cal_upcoming = results.get("cal_upcoming", [])
        legis_upcoming = results.get("legis_upcoming", [])
        legislation_stats = results.get("legislation_stats", {"total_passed": 0, "this_week": 0, "this_month": 0, "last_30_days": 0})
        budget_stats = results.get("budget_stats", {"fiscal_year": None, "total_budget": None, "total_spent": None, "percentage_spent": None})
        
        boards_upcoming = []
        boards_upcoming.extend([
            {
                "title": i.get("title"),
                "date": i.get("date_display"),
                "location": i.get("location"),
                "link": i.get("link"),
            }
            for i in cal_upcoming
        ])
        boards_upcoming.extend([
            {
                "title": i.get("title"),
                "date": i.get("date_display"),
                "location": i.get("location"),
                "link": i.get("link"),
            }
            for i in legis_upcoming
        ])
        try:
            boards_upcoming.sort(key=lambda x: x.get("date") or "")
        except Exception:
            pass
        boards_upcoming = boards_upcoming[:8]

        # Events from aggregator (already fetched in parallel)
        agg = results.get("agg", {})
        agg_items = agg.get("items", [])
        # Limit to most recent 20 items for homepage performance (reduced from 30)
        agg_items = agg_items[:20]
        
        unified_events: List[Dict[str, Any]] = []
        for it in agg_items:
            category = it.get("category") or "news"
            if category in {"events", "city_events", "city_calendar_items", "music_arts"}:
                source_meta = it.get("source") or {}
                unified_events.append({
                    "title": it.get("title"),
                    "link": it.get("link"),
                    "summary": it.get("summary"),
                    "source": source_meta.get("name") or "Source",
                    "date_iso": it.get("date"),
                    "location": it.get("location"),
                })

        # Filter to current week (starting on Sunday)
        def within_current_week(iso_str: str) -> bool:
            try:
                if not iso_str:
                    return False
                dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(tz)
                days_to_sunday = (today.weekday() + 1) % 7
                start_of_week = today - timedelta(days=days_to_sunday)
                end_of_week = start_of_week + timedelta(days=7)
                return start_of_week <= dt < end_of_week
            except Exception:
                return False

        week_events = [e for e in unified_events if within_current_week(e.get("date_iso") or "")]

        # Merge manual events into the same "this week" feed
        for it in _load_manual_events():
            iso = it.get("date_iso") or ""
            if not within_current_week(iso):
                continue
            week_events.append({
                "title": it.get("title"),
                "link": it.get("link") or "",
                "summary": it.get("summary") or "",
                "source": it.get("source") or "Manual",
                "date_iso": iso,
                "location": it.get("location") or "",
            })

        # Only sort if we have events (early return optimization)
        if week_events:
            week_events.sort(key=lambda x: x.get("date_iso", ""))
            week_events = week_events[:14]

        # Fallback to stub events
        if not week_events:
            fallback = [
                {
                    "title": e.title,
                    "link": e.link,
                    "summary": e.description,
                    "source": "Local Events",
                    "date_iso": e.start.astimezone(ZoneInfo("UTC")).isoformat(),
                    "location": e.location,
                }
                for e in events_service.get_upcoming_events(tz=tz, max_events=8)
                if within_current_week(e.start.astimezone(ZoneInfo("UTC")).isoformat())
            ]
            week_events = sorted(fallback, key=lambda i: i.get("date_iso", ""))

        # Build 7-day grid (starting on Sunday)
        days_to_sunday = (today.weekday() + 1) % 7
        start_of_week = today - timedelta(days=days_to_sunday)
        week_start_date = start_of_week.strftime("%b %d")
        week_grid = []
        
        for i in range(7):
            d = (start_of_week + timedelta(days=i)).date()
            label = (start_of_week + timedelta(days=i)).strftime("%a")
            items_for_day = []
            
            for ev in week_events:
                iso = ev.get("date_iso")
                if not iso:
                    continue
                try:
                    dt_local = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(tz)
                    if dt_local.date() == d:
                        time_str = dt_local.strftime("%I:%M %p").lstrip("0")
                        items_for_day.append({
                            "time": time_str,
                            "title": ev.get("title"),
                            "link": ev.get("link"),
                            "location": ev.get("location") or "",
                            "source": ev.get("source") or "",
                            "date": dt_local.strftime("%Y-%m-%d %I:%M %p"),
                            "summary": ev.get("summary") or "",
                        })
                except Exception:
                    continue
            
            week_grid.append({"label": label, "items": items_for_day[:3]})

        # Format sunrise/sunset times
        if weather:
            weather = weather.copy()  # Don't modify the original
            if weather.get("sunrise"):
                weather["sunrise"] = format_sun_time(weather["sunrise"])
            if weather.get("sunset"):
                weather["sunset"] = format_sun_time(weather["sunset"])
        
        html = render_template(
            "index.html",
            app_name=app.config["APP_NAME"],
            date_str=date_str,
            center_lat=lat,
            center_lon=lon,
            weather=weather,
            nws_alerts=nws_alerts[:3],
            air_quality=air_quality,
            tax_info=tax_info,
            boards_upcoming=boards_upcoming,
            week_grid=week_grid,
            week_start_date=week_start_date,
            hours_all=hours_all,
            trivia_items=trivia_items,
            legislation_stats=legislation_stats,
            budget_stats=budget_stats,
        )
        _index_html_cache.set("index_html", html)
        resp = Response(html, mimetype="text/html")
        resp.headers["X-Elm-Cache"] = "MISS"
        return resp

    @app.route("/about")
    def about():
        return render_template("about.html", app_name=app.config["APP_NAME"])

    @app.route("/feeds")
    def feeds_api():
        data = aggregate_all()
        return jsonify(data)

    @app.route("/api/nws/alerts")
    def api_nws_alerts():
        zone = request.args.get("zone", "ctz010")
        data = nws_service.fetch_nws_alerts(zone=zone)
        return jsonify({"zone": zone, "alerts": data})

    @app.route("/api/tides")
    def api_tides():
        station = request.args.get("station", "8465705")
        day = request.args.get("date", "today")
        data = tides_service.fetch_tides(station=station, day=day)
        return jsonify(data)

    @app.route("/feeds.rss")
    def feeds_rss():
        """RSS feed output for feed readers"""
        data = aggregate_all()
        items = data.get("items", [])[:20]
        
        rss_items = []
        for it in items:
            pub_date = it.get("date", "")
            try:
                dt = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                pub_date = dt.strftime("%a, %d %b %Y %H:%M:%S +0000")
            except Exception:
                pub_date = ""
            
            title = str(it.get('title', '')).replace(']]>', ']]&gt;')
            link = str(it.get('link', ''))
            summary = str(it.get('summary', '')).replace(']]>', ']]&gt;')
            
            rss_items.append(f"""    <item>
      <title><![CDATA[{title}]]></title>
      <link>{link}</link>
      <description><![CDATA[{summary}]]></description>
      <pubDate>{pub_date}</pubDate>
    </item>""")
        
        build_date = datetime.now(ZoneInfo("UTC")).strftime("%a, %d %b %Y %H:%M:%S +0000")
        items_xml = "\n".join(rss_items)
        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Elm City Daily</title>
    <link>https://elmcitydaily.com</link>
    <description>Your Daily Civic Digest for New Haven, CT</description>
    <lastBuildDate>{build_date}</lastBuildDate>
{items_xml}
  </channel>
</rss>"""
        return Response(rss, mimetype="application/rss+xml")

    @app.route("/api/events/week")
    def api_events_week():
        """API endpoint for events in a specific week (starting on Sunday)"""
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz)
        week_offset = int(request.args.get("offset", 0))
        
        days_to_sunday = (today.weekday() + 1) % 7
        start_of_week = today - timedelta(days=days_to_sunday) + timedelta(weeks=week_offset)
        end_of_week = start_of_week + timedelta(days=7)
        
        agg = aggregate_all()
        agg_items = agg.get("items", [])
        
        week_events = []
        for it in agg_items:
            category = it.get("category") or "news"
            if category not in {"events", "city_events", "city_calendar_items", "music_arts"}:
                continue
            date_iso = it.get("date")
            if not date_iso:
                continue
            try:
                dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(tz)
                if start_of_week <= dt < end_of_week:
                    week_events.append({
                        "title": it.get("title"),
                        "link": it.get("link"),
                        "location": it.get("location") or "",
                        "source": (it.get("source") or {}).get("name") or "Source",
                        "date_iso": date_iso,
                        "summary": it.get("summary") or "",
                    })
            except Exception:
                continue

        # Merge manual events
        for it in _load_manual_events():
            date_iso = it.get("date_iso") or ""
            if not date_iso:
                continue
            try:
                dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00")).astimezone(tz)
                if start_of_week <= dt < end_of_week:
                    week_events.append({
                        "title": it.get("title"),
                        "link": it.get("link") or "",
                        "location": it.get("location") or "",
                        "source": it.get("source") or "Manual",
                        "date_iso": date_iso,
                        "summary": it.get("summary") or "",
                    })
            except Exception:
                continue
        
        # Fallback
        if not week_events:
            for e in events_service.get_upcoming_events(tz=tz, max_events=20):
                ev_dt = e.start
                if start_of_week <= ev_dt < end_of_week:
                    week_events.append({
                        "title": e.title,
                        "link": e.link or "",
                        "location": e.location,
                        "source": "Local Events",
                        "date_iso": ev_dt.astimezone(ZoneInfo("UTC")).isoformat(),
                        "summary": e.description,
                    })
        
        # Only sort if we have events
        if week_events:
            week_events.sort(key=lambda x: x.get("date_iso", ""))
        
        # Build grid
        week_grid = []
        for i in range(7):
            d = (start_of_week + timedelta(days=i)).date()
            label = (start_of_week + timedelta(days=i)).strftime("%a")
            items_for_day = []
            for ev in week_events:
                try:
                    dt_local = datetime.fromisoformat(ev["date_iso"].replace("Z", "+00:00")).astimezone(tz)
                    if dt_local.date() == d:
                        time_str = dt_local.strftime("%I:%M %p").lstrip("0")
                        items_for_day.append({
                            "time": time_str,
                            "title": ev["title"],
                            "link": ev["link"],
                            "location": ev["location"],
                            "source": ev["source"],
                            "date": dt_local.strftime("%Y-%m-%d %I:%M %p"),
                            "summary": ev["summary"],
                        })
                except Exception:
                    continue
            week_grid.append({"label": label, "items": items_for_day[:3]})
        
        return jsonify({
            "week_grid": week_grid,
            "week_start_date": start_of_week.strftime("%b %d"),
            "week_offset": week_offset,
        })

    # Legislation Tracker Routes
    tracker = LegislationTracker()
    
    @app.route("/legislation")
    def legislation_tracker():
        """Track passed legislation in New Haven"""
        try:
            # Get passed legislation from last 90 days
            legislation = tracker.get_passed_legislation(days_back=90, limit=500)
            
            # Group by week and month
            weekly = tracker.group_by_week(legislation)
            monthly = tracker.group_by_month(legislation)
            monthly_counts = tracker.get_monthly_counts(legislation)
            stats = tracker.get_stats(legislation)
            
            return render_template(
                "legislation/tracker.html",
                app_name=app.config["APP_NAME"],
                legislation=legislation,
                weekly=weekly,
                monthly=monthly,
                monthly_counts=monthly_counts,
                stats=stats,
            )
        except Exception as e:
            app.logger.error(f"Error fetching legislation: {e}")
            return render_template(
                "legislation/tracker.html",
                app_name=app.config["APP_NAME"],
                legislation=[],
                weekly={},
                monthly={},
                monthly_counts=[],
                stats={"total_passed": 0, "this_week": 0, "this_month": 0, "last_30_days": 0},
                error=str(e)
            )
    
    @app.route("/api/legislation")
    def api_legislation():
        """API endpoint for legislation data"""
        try:
            legislation = tracker.get_passed_legislation(days_back=90, limit=500)
            weekly = tracker.group_by_week(legislation)
            monthly = tracker.group_by_month(legislation)
            monthly_counts = tracker.get_monthly_counts(legislation)
            stats = tracker.get_stats(legislation)
            
            return jsonify({
                "legislation": legislation,
                "weekly": weekly,
                "monthly": monthly,
                "monthly_counts": monthly_counts,
                "stats": stats
            })
        except Exception as e:
            app.logger.error(f"Error in API: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Budget Tracker Routes
    budget_tracker = BudgetTracker()
    
    @app.route("/budget")
    def budget_tracker_page():
        """Budget spending tracker page"""
        try:
            summary = budget_tracker.fetch_budget_summary()
            categories = budget_tracker.get_spending_by_category()
            stats = budget_tracker.get_budget_stats()
            
            return render_template(
                "budget/tracker.html",
                app_name=app.config["APP_NAME"],
                summary=summary,
                categories=categories,
                stats=stats,
            )
        except Exception as e:
            app.logger.error(f"Error fetching budget data: {e}")
            return render_template(
                "budget/tracker.html",
                app_name=app.config["APP_NAME"],
                summary={},
                categories={"categories": []},
                stats={},
                error=str(e)
            )
    
    @app.route("/api/budget")
    def api_budget():
        """API endpoint for budget data"""
        try:
            summary = budget_tracker.fetch_budget_summary()
            categories = budget_tracker.get_spending_by_category()
            stats = budget_tracker.get_budget_stats()
            
            return jsonify({
                "summary": summary,
                "categories": categories,
                "stats": stats
            })
        except Exception as e:
            app.logger.error(f"Error in budget API: {e}")
            return jsonify({"error": str(e)}), 500

    return app


app = create_app()

if __name__ == "__main__":
    import argparse
    import os
    import socket

    def find_available_port(preferred_port: int, host: str = "0.0.0.0", max_tries: int = 50) -> int:
        port = preferred_port
        for _ in range(max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind((host, port))
                    return port
                except OSError:
                    port += 1
        return preferred_port

    parser = argparse.ArgumentParser(description="Run Elm City Daily Flask app.")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "5000")))
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    chosen_port = find_available_port(args.port, host=args.host)
    if chosen_port != args.port:
        logging.info("Port %s in use; using %s", args.port, chosen_port)

    app.run(host=args.host, port=chosen_port, debug=args.debug)
