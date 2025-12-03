# Elm City Daily

A single-page local dashboard for New Haven, CT.

## InfoNewHaven Feeds Integration

This app aggregates RSS and iCal feeds from InfoNewHaven.com and exposes JSON endpoints.

### Currently used feeds

- Working (pulled today):
  - Focus is now on primary public sources for civic information. Third‑party news feeds are not used in the dashboard UI.
- Disabled (not pulling):
  - City of New Haven — News RSS (`https://www.newhavenct.gov/Home/Components/News/RSS`) — 403
  - City of New Haven — Calendar Event RSS (`https://www.newhavenct.gov/Home/Components/Calendar/Event/RSS`) — 403
  - City of New Haven — Calendar Item RSS (`https://www.newhavenct.gov/Home/Components/Calendar/Item/RSS`) — 403
  - InfoNewHaven Events iCal (`https://www.infonewhaven.com/things-to-do/new-haven-events-calendar/?ical=1`) — blocked by JS challenge (Sucuri), not fetchable server-side.

Notes:
- If feeds yield no dated items for the week, a small local stub of upcoming events is shown as a fallback.

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

### Configuration notes
- Third‑party news is disabled in the dashboard. `FEED_URLS` can be left empty or customized for your own use; it is not displayed in the UI.

## Primary sources used for civics
- Legistar Web API (City legislative data)
  - Base: `https://webapi.legistar.com/v1/<city>` (default: `newhaven`)
  - Env overrides:
    - `LEGISTAR_BASE` (API base)
    - `LEGISTAR_UI_HOST` (public UI host used to form detail links; default `https://newhavenct.legistar.com`)
- CT Open Data (Tax/Mill rate)
  - Dataset URL (env): `TAX_RATE_URL` — e.g. `https://data.ct.gov/resource/<dataset>.json`
  - The code queries `?municipality=New%20Haven` and uses the latest fiscal year returned.

In the right rail (“City by the Numbers”) we show:
- Matters counted since the earliest retrieved date window
- Adopted vs. failed/withdrawn counts
- Heuristic count of “projects in-process” (matters with types containing Capital/Project/Development/Construction and not yet adopted/failed)
- Latest mill rate and fiscal year if available