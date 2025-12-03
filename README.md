# Elm City Daily

A single-page local dashboard for New Haven, CT.

## InfoNewHaven Feeds Integration

This app aggregates RSS and iCal feeds from InfoNewHaven.com and exposes JSON endpoints.

Endpoints:
- `/feeds` — Aggregated and normalized feed items. Optional `?category=` filter supports: `who_knew_blog`, `food_drink`, `music_arts`, `events`, `news`.
- `/feeds/raw` — Same as `/feeds` without filtering, for debugging.
- `/feeds/view` — Minimal Tailwind-based view with category filters, powered by `/feeds`.

Attribution:

This product uses feeds provided by InfoNewHaven.com — Visit | Stay | Play | Live Here in the Elm City.

Each item includes:
```
{
  "title": "...",
  "link": "...",
  "summary": "...",
  "date": "ISO8601",
  "category": "who_knew_blog|food_drink|music_arts|events|news",
  "source": { "name": "InfoNewHaven.com", "url": "https://www.infonewhaven.com" },
  "credit": {
    "source": "InfoNewHaven.com",
    "url": "https://www.infonewhaven.com",
    "note": "All RSS/iCal feeds are provided courtesy of InfoNewHaven.com — Visit | Stay | Play | Live Here in the Elm City."
  }
}
```

### Adding new categories
- Add an entry to `feeds/sources.py` in `RSS_SOURCES` or `ICAL_SOURCES`.
- For RSS categories, ensure `feeds/feed_parser.py` maps `source_key` to the desired normalized `category`.

### Caching
The aggregator uses a simple in-process TTL cache (10 minutes) defined in `utils/cache.py`.
To pre-warm via cron:
```bash
python refresh_feeds.py
```

### Deploy notes
- App auto-selects an available port if the preferred one is busy. You can set `PORT` or pass `--port`.
- For production behind a reverse proxy, bind `--host 0.0.0.0` and let the proxy terminate TLS.

## Run locally

Create a venv and install:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Copy env and run:
```bash
cp .env.example .env
python app.py --port 5000
```

Open http://127.0.0.1:5000/ for the dashboard or http://127.0.0.1:5000/feeds/view for the feed browser.