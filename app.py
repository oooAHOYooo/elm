import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List

from dotenv import load_dotenv
from flask import Flask, render_template
from flask import jsonify, request

from config import Config
from services import events as events_service
from services import rss as rss_service
from services.civics import (
    fetch_recent_matters,
    compute_civics_stats,
    fetch_tax_rate,
    fetch_city_calendar,
    fetch_legistar_events,
)
from services import weather as weather_service
from services import nws as nws_service
from services import tides as tides_service
from feeds.aggregator import aggregate_all, aggregate_filtered


load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging setup
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.logger.setLevel(logging.INFO)
    # Register blueprints (none currently)

    @app.route("/")
    def index():
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz)
        date_str = today.strftime("%A, %B %d, %Y")
        time_str = today.strftime("%I:%M %p")

        # Fetch data from services
        feeds: List[str] = app.config["FEED_URLS"]
        per_feed_limit: int = int(app.config["RSS_PER_FEED_LIMIT"])
        overall_limit: int = int(app.config["RSS_OVERALL_LIMIT"])
        timeout: int = int(app.config["REQUEST_TIMEOUT"])

        # Policy: avoid third-party news; only primary sources.
        # If FEED_URLS is empty, skip entirely.
        if feeds:
            articles = rss_service.fetch_rss_feeds(
                feed_urls=feeds,
                per_feed_limit=per_feed_limit,
                overall_limit=overall_limit,
                request_timeout=timeout,
            )
        else:
            articles = []

        # Pull InfoNewHaven + City feeds and merge
        agg = aggregate_all()
        agg_items = agg.get("items", [])

        # Normalize aggregator items to match template expectations
        def iso_to_display(iso_str: str) -> str:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
                return dt.astimezone(tz).strftime("%Y-%m-%d %I:%M %p")
            except Exception:
                return ""

        unified_news: List[Dict[str, Any]] = []
        unified_events: List[Dict[str, Any]] = []

        # Existing RSS articles as news
        for a in articles:
            unified_news.append(
                {
                    "title": a.get("title"),
                    "link": a.get("link"),
                    "summary": a.get("summary"),
                    "source": a.get("source"),
                    "published": a.get("published"),
                    "published_display": a.get("published_display"),
                    "category": "news",
                    "image": a.get("image"),
                }
            )

        # Aggregator items (news + events)
        for it in agg_items:
            category = it.get("category") or "news"
            source_meta = it.get("source") or {}
            source_name = source_meta.get("name") or "Source"
            date_iso = it.get("date")
            item = {
                "title": it.get("title"),
                "link": it.get("link"),
                "summary": it.get("summary"),
                "source": source_name,
                "published": None,
                "published_display": iso_to_display(date_iso) if date_iso else "",
                "category": category,
                "image": None,
                "date_iso": date_iso,
                "location": it.get("location"),
            }
            # Treat culture/music posts as events for now to surface weekly happenings
            if category in {"events", "city_events", "city_calendar_items", "music_arts"}:
                unified_events.append(item)
            else:
                unified_news.append(item)

        # De-duplicate by link
        seen_links = set()
        deduped_news: List[Dict[str, Any]] = []
        for i in unified_news:
            link = i.get("link")
            if link and link in seen_links:
                continue
            if link:
                seen_links.add(link)
            deduped_news.append(i)

        # Sort by published_display/iso recency; fall back to insertion order
        def sort_key(i: Dict[str, Any]):
            from datetime import datetime
            try:
                # Prefer iso via published_display parsed back in local tz
                disp = i.get("published_display")
                if disp:
                    # Parse with local tz format used above
                    return datetime.strptime(disp, "%Y-%m-%d %I:%M %p").timestamp()
            except Exception:
                pass
            try:
                pub = i.get("published")
                if pub:
                    return pub.timestamp()
            except Exception:
                pass
            return 0.0

        deduped_news.sort(key=sort_key, reverse=True)

        # Compact selection for dashboard (news suppressed; keep placeholders)
        featured_story = None
        supporting_items: List[Dict[str, Any]] = []
        right_rail_items: List[Dict[str, Any]] = []
        bottom_news: List[Dict[str, Any]] = []

        lat = float(app.config["WEATHER_LAT"])
        lon = float(app.config["WEATHER_LON"])
        weather: Dict[str, Any] = weather_service.fetch_weather(
            lat=lat, lon=lon, request_timeout=timeout
        )
        # NWS alerts + forecast (compact dashboard snippets)
        nws_alerts = nws_service.fetch_nws_alerts(zone="ctz010")
        nws_fc = nws_service.fetch_nws_forecast(lat=lat, lon=lon)
        nws_periods = nws_fc.get("periods", [])[:2] if nws_fc else []

        # Compute simple daypart temperatures from hourly forecast (local time)
        daypart_temps: Dict[str, Any] = {}
        try:
            from datetime import datetime as _dt
            from zoneinfo import ZoneInfo as _ZoneInfo
            hourly = (nws_fc or {}).get("hourly", []) or []
            buckets = {
                "morning": [],
                "afternoon": [],
                "evening": [],
                "night": [],
            }
            for h in hourly:
                t_iso = h.get("startTime")
                temp = h.get("temperature")
                if t_iso is None or temp is None:
                    continue
                try:
                    dt_local = _dt.fromisoformat(t_iso.replace("Z", "+00:00")).astimezone(_ZoneInfo("America/New_York"))
                    hour = dt_local.hour
                    # morning 6–11, afternoon 12–17, evening 18–21, night 22–5
                    if 6 <= hour <= 11:
                        buckets["morning"].append(temp)
                    elif 12 <= hour <= 17:
                        buckets["afternoon"].append(temp)
                    elif 18 <= hour <= 21:
                        buckets["evening"].append(temp)
                    else:
                        buckets["night"].append(temp)
                except Exception:
                    continue
            for k, vals in buckets.items():
                if vals:
                    daypart_temps[k] = round(sum(vals) / len(vals))
                else:
                    daypart_temps[k] = None
        except Exception:
            daypart_temps = {"morning": None, "afternoon": None, "evening": None, "night": None}

        # This week's events (next 7 days)
        def within_next_seven_days(iso_str: str) -> bool:
            try:
                from datetime import datetime, timedelta
                if not iso_str:
                    return False
                dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(tz)
                return today <= dt <= (today + timedelta(days=7))
            except Exception:
                return False

        week_events = [e for e in unified_events if within_next_seven_days(e.get("date_iso") or "")]
        # sort ascending by date within the week
        def week_sort_key(i: Dict[str, Any]):
            try:
                from datetime import datetime
                iso = i.get("date_iso")
                if iso:
                    return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
            except Exception:
                pass
            return 0.0
        week_events.sort(key=week_sort_key)
        week_events = week_events[:14]

        # Fallback to stub events if no week events from feeds
        if not week_events:
            fallback = [
                {
                    "title": e.title,
                    "link": e.link,
                    "summary": e.description,
                    "source": "Local Events",
                    "published": None,
                    "published_display": e.start.strftime("%Y-%m-%d %I:%M %p"),
                    "category": "events",
                    "image": None,
                    "location": e.location,
                    "date_iso": e.start.astimezone(ZoneInfo("UTC")).isoformat(),
                }
                for e in events_service.get_upcoming_events(tz=tz, max_events=8)
                if within_next_seven_days(e.start.astimezone(ZoneInfo("UTC")).isoformat())
            ]
            week_events = sorted(fallback, key=lambda i: i.get("date_iso", ""))

        # Build compact 7-day grid starting Monday
        from datetime import timedelta
        start_of_week = today - timedelta(days=today.weekday())
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
                        items_for_day.append(
                            {
                                "time": dt_local.strftime("%-I:%M %p") if hasattr(dt_local, "strftime") else "",
                                "title": ev.get("title"),
                                "link": ev.get("link"),
                                "location": ev.get("location") or "",
                                "source": ev.get("source") or "",
                                "date": ev.get("published_display") or dt_local.strftime("%Y-%m-%d %I:%M %p"),
                                "summary": ev.get("summary") or "",
                            }
                        )
                except Exception:
                    continue
            # keep it compact: cap to first 2 items
            week_grid.append({"label": label, "items": items_for_day[:2]})

        # Prefer aggregator events; fallback to stub if none
        upcoming_events = unified_events[:6] if unified_events else [
            {
                "title": e.title,
                "link": e.link,
                "summary": e.description,
                "source": "Local Events",
                "published": None,
                "published_display": e.start.strftime("%Y-%m-%d %I:%M %p"),
                "category": "events",
                "image": None,
                "location": e.location,
                "start": e.start,
            }
            for e in events_service.get_upcoming_events(tz=tz, max_events=6)
        ]

        categories = [
            {"key": "news", "label": "News"},
            {"key": "events", "label": "Events"},
            {"key": "weather", "label": "Weather"},
        ]

        bottom_strip_items = []
        # Mix events compactly (no news)
        # Add up to 2 weather cards from NWS
        for p in (nws_periods or [])[:2]:
            if len(bottom_strip_items) >= 8:
                break
            bottom_strip_items.append(
                {
                    "category": "weather",
                    "title": f"{p.get('name')}: {p.get('temperature')}{p.get('temperatureUnit')}",
                    "summary": p.get("shortForecast"),
                }
            )
        for ev in upcoming_events[:6 - len(bottom_strip_items)]:
            ev2 = dict(ev)
            ev2["category"] = "events"
            bottom_strip_items.append(ev2)

        # Primary-source civics: recent council actions and stats
        city_slug = "newhaven"
        matters = fetch_recent_matters(city_slug=city_slug, days_back=120, limit=250)
        civics_actions = [
            {
                "title": f"{m.get('file', '')} · {m.get('title')}",
                "link": m.get("link"),
                "source": f"{m.get('status', '')}",
                "published_display": m.get("date_display"),
                "location": m.get("type", ""),
            }
            for m in matters[:12]
        ]
        civics_stats = compute_civics_stats(matters)
        tax_info = fetch_tax_rate(municipality="New Haven")

        # Public RSS history by category (compact list for dropdowns)
        feed_history: Dict[str, List[Dict[str, Any]]] = {}
        for it in agg_items:
            cat = it.get("category") or "news"
            if cat not in {"who_knew_blog", "food_drink", "music_arts", "events"}:
                continue
            lst = feed_history.setdefault(cat, [])
            lst.append(
                {
                    "title": it.get("title"),
                    "date": it.get("date"),
                    "link": it.get("link"),
                    "source": (it.get("source") or {}).get("name"),
                }
            )
        # Trim history lists
        for k in list(feed_history.keys()):
            feed_history[k] = feed_history[k][:20]

        # Boards & Commissions upcoming (calendar JSON + Legistar events)
        cal_upcoming = fetch_city_calendar(limit=6)
        legis_upcoming = fetch_legistar_events(city_slug=city_slug, limit=6)
        boards_upcoming = []
        boards_upcoming.extend(
            [
                {
                    "title": i.get("title"),
                    "date": i.get("date_display"),
                    "location": i.get("location"),
                    "source": "City Calendar",
                    "link": i.get("link"),
                }
                for i in cal_upcoming
            ]
        )
        boards_upcoming.extend(
            [
                {
                    "title": i.get("title"),
                    "date": i.get("date_display"),
                    "location": i.get("location"),
                    "source": i.get("body") or "Legistar",
                    "link": i.get("link"),
                }
                for i in legis_upcoming
            ]
        )
        # sort by date string to keep near-future first
        try:
            boards_upcoming.sort(key=lambda x: x.get("date") or "")
        except Exception:
            pass
        boards_upcoming = boards_upcoming[:8]

        return render_template(
            "index.html",
            app_name=app.config["APP_NAME"],
            date_str=date_str,
            center_lat=lat,
            center_lon=lon,
            featured_story=featured_story,
            supporting_items=supporting_items,
            right_rail_items=right_rail_items,
            bottom_strip_items=bottom_strip_items,
            weather=weather,
            nws_alerts=nws_alerts[:3],
            nws_periods=nws_periods,
            daypart_temps=daypart_temps,
            week_events=week_events,
            events=upcoming_events,
            categories=categories,
            civics_actions=civics_actions,
            civics_stats=civics_stats,
            tax_info=tax_info,
            feed_history=feed_history,
            week_grid=week_grid,
            time_str=time_str,
            boards_upcoming=boards_upcoming,
        )

    @app.route("/feeds")
    def feeds_api():
        # Optional ?category=events|who_knew_blog|food_drink|music_arts|news
        category = request.args.get("category")
        data = aggregate_filtered(category=category) if category else aggregate_all()
        return jsonify(data)

    @app.route("/feeds/raw")
    def feeds_raw():
        # Debugging endpoint returns full aggregate
        return jsonify(aggregate_all())

    @app.route("/feeds/view")
    def feeds_view():
        # Minimal page that fetches /feeds and shows category filters
        return render_template("feeds.html", app_name=app.config["APP_NAME"])

    @app.route("/about")
    def about():
        return render_template("about.html", app_name=app.config["APP_NAME"])

    @app.route("/api/nws/alerts")
    def api_nws_alerts():
        zone = request.args.get("zone", "ctz010")
        data = nws_service.fetch_nws_alerts(zone=zone)
        return jsonify({"zone": zone, "alerts": data})

    @app.route("/api/nws/forecast")
    def api_nws_forecast():
        lat = float(request.args.get("lat", app.config["WEATHER_LAT"]))
        lon = float(request.args.get("lon", app.config["WEATHER_LON"]))
        data = nws_service.fetch_nws_forecast(lat=lat, lon=lon)
        return jsonify({"lat": lat, "lon": lon, **data})

    @app.route("/api/tides")
    def api_tides():
        station = request.args.get("station", "8465705")
        day = request.args.get("date", "today")
        data = tides_service.fetch_tides(station=station, day=day)
        return jsonify(data)

    return app


app = create_app()

if __name__ == "__main__":
    import argparse
    import os
    import socket

    def find_available_port(preferred_port: int, host: str = "0.0.0.0", max_tries: int = 50) -> int:
        """
        Try preferred_port; if unavailable, search sequentially for a free port.
        """
        port = preferred_port
        for _ in range(max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                try:
                    sock.bind((host, port))
                    # success; socket closes immediately, freeing port for Flask to bind
                    return port
                except OSError:
                    port += 1
        return preferred_port

    parser = argparse.ArgumentParser(description="Run Elm City Daily Flask app.")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"), help="Host interface to bind")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PORT", os.getenv("FLASK_RUN_PORT", "5000"))),
        help="Port to bind; will search for next free port if in use",
    )
    parser.add_argument("--debug", action="store_true", help="Enable Flask debug mode")
    parser.add_argument("--no-debug", action="store_true", help="Force disable Flask debug mode")
    args = parser.parse_args()

    # Resolve debug flag precedence: CLI > env/config
    debug_default = bool(app.config.get("DEBUG", False))
    debug_resolved = debug_default
    if args.debug:
        debug_resolved = True
    if args.no_debug:  # type: ignore[attr-defined]
        debug_resolved = False

    desired_port = args.port
    chosen_port = find_available_port(desired_port, host=args.host, max_tries=200)
    if chosen_port != desired_port:
        logging.info("Port %s is in use; switching to available port %s", desired_port, chosen_port)

    app.run(host=args.host, port=chosen_port, debug=debug_resolved)


