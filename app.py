import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any, Dict, List

from dotenv import load_dotenv
from flask import Flask, render_template

from config import Config
from services import events as events_service
from services import rss as rss_service
from services import weather as weather_service


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

    @app.route("/")
    def index():
        tz = ZoneInfo("America/New_York")
        today = datetime.now(tz)
        date_str = today.strftime("%A, %B %d, %Y")

        # Fetch data from services
        feeds: List[str] = app.config["FEED_URLS"]
        per_feed_limit: int = int(app.config["RSS_PER_FEED_LIMIT"])
        overall_limit: int = int(app.config["RSS_OVERALL_LIMIT"])
        timeout: int = int(app.config["REQUEST_TIMEOUT"])

        articles = rss_service.fetch_rss_feeds(
            feed_urls=feeds,
            per_feed_limit=per_feed_limit,
            overall_limit=overall_limit,
            request_timeout=timeout,
        )

        featured_story = articles[0] if articles else None
        supporting_items = articles[1:6] if len(articles) > 1 else []
        right_rail_items = articles[6:10] if len(articles) > 6 else []
        bottom_strip_items = articles[:12] if articles else []

        lat = float(app.config["WEATHER_LAT"])
        lon = float(app.config["WEATHER_LON"])
        weather: Dict[str, Any] = weather_service.fetch_weather(
            lat=lat, lon=lon, request_timeout=timeout
        )

        upcoming_events = events_service.get_upcoming_events(tz=tz, max_events=6)

        categories = [
            {"key": "news", "label": "News"},
            {"key": "events", "label": "Events"},
            {"key": "weather", "label": "Weather"},
        ]

        return render_template(
            "index.html",
            app_name=app.config["APP_NAME"],
            date_str=date_str,
            featured_story=featured_story,
            supporting_items=supporting_items,
            right_rail_items=right_rail_items,
            bottom_strip_items=bottom_strip_items,
            weather=weather,
            events=upcoming_events,
            categories=categories,
        )

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


