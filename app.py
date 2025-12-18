"""
Elm City Daily — MVP Newspaper Dashboard
A simplified civic dashboard for New Haven, CT
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any, Dict, List

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

load_dotenv()

# Thread pool for parallel API calls
_executor = ThreadPoolExecutor(max_workers=6)


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
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz)
        date_str = today.strftime("%A, %B %d, %Y")
        timeout: int = int(app.config["REQUEST_TIMEOUT"])
        lat = float(app.config["WEATHER_LAT"])
        lon = float(app.config["WEATHER_LON"])

        # Parallel API fetching for speed
        airnow_key = app.config.get("AIRNOW_API_KEY", "")
        
        futures = {
            _executor.submit(weather_service.fetch_weather, lat, lon, timeout): "weather",
            _executor.submit(nws_service.fetch_nws_alerts, "ctz010"): "nws_alerts",
            _executor.submit(aqi_service.fetch_air_quality, lat, lon, airnow_key or None): "air_quality",
            _executor.submit(fetch_tax_rate, "New Haven"): "tax_info",
            _executor.submit(fetch_city_calendar, 6): "cal_upcoming",
            _executor.submit(fetch_legistar_events, "newhaven", 6): "legis_upcoming",
            _executor.submit(aggregate_all): "agg",
        }
        
        results = {}
        for future in as_completed(futures, timeout=10):
            key = futures[future]
            try:
                results[key] = future.result()
            except Exception as e:
                app.logger.warning(f"Failed to fetch {key}: {e}")
                results[key] = {} if key in ("weather", "air_quality", "tax_info", "agg") else []
        
        weather = results.get("weather", {})
        nws_alerts = results.get("nws_alerts", [])
        air_quality = results.get("air_quality", {})
        tax_info = results.get("tax_info", {})
        cal_upcoming = results.get("cal_upcoming", [])
        legis_upcoming = results.get("legis_upcoming", [])
        
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

        # Filter to current week
        def within_current_week(iso_str: str) -> bool:
            try:
                if not iso_str:
                    return False
                dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(tz)
                start_of_week = today - timedelta(days=today.weekday())
                end_of_week = start_of_week + timedelta(days=7)
                return start_of_week <= dt < end_of_week
            except Exception:
                return False

        week_events = [e for e in unified_events if within_current_week(e.get("date_iso") or "")]
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

        # Build 7-day grid
        start_of_week = today - timedelta(days=today.weekday())
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

        return render_template(
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
        )

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
            
            rss_items.append(f"""    <item>
      <title><![CDATA[{it.get('title', '')}]]></title>
      <link>{it.get('link', '')}</link>
      <description><![CDATA[{it.get('summary', '')}]]></description>
      <pubDate>{pub_date}</pubDate>
    </item>""")
        
        rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Elm City Daily</title>
    <link>https://elmcitydaily.com</link>
    <description>Your Daily Civic Digest for New Haven, CT</description>
    <lastBuildDate>{datetime.now(ZoneInfo("UTC")).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
{chr(10).join(rss_items)}
  </channel>
</rss>"""
        return Response(rss, mimetype="application/rss+xml")

    @app.route("/api/events/week")
    def api_events_week():
        """API endpoint for events in a specific week"""
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz)
        week_offset = int(request.args.get("offset", 0))
        
        start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
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
