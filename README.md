# 🌳 Elm City Daily

**A real-time civic dashboard for New Haven, Connecticut — The Elm City**

Elm City Daily is a single-page, live-feed driven dashboard that aggregates civic data, weather, events, and community information from authoritative primary sources. Built by public servants, for the public good.

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.10+-blue) ![Flask](https://img.shields.io/badge/flask-3.0-lightgrey)

---

## 📋 Current Features

### 🌤️ Weather & Environment

| Feature | Source | Description |
|---------|--------|-------------|
| **Current Conditions** | Open-Meteo API | Real-time temperature, wind speed/direction, weather codes with emoji icons |
| **Daily High/Low** | Open-Meteo API | Today's forecast highs and lows |
| **Daypart Temperatures** | NWS Hourly | Morning, afternoon, evening, and night temperature breakdowns |
| **NWS Alerts** | weather.gov CAP RSS | Active National Weather Service alerts for zone CTZ010 (New Haven) |
| **NWS Forecast** | api.weather.gov | 7-day and hourly forecasts from the National Weather Service |
| **Tide Predictions** | NOAA CO-OPS | High/low tide times and heights for New Haven Harbor (Station 8465705) |
| **Air Quality Index** | EPA AirNow API | Real-time AQI with color-coded badges, health advice, and pollutant info |
| **Unit Conversion** | Client-side | Toggle between Fahrenheit and Celsius |

### 🏛️ Civic Data & Government

| Feature | Source | Description |
|---------|--------|-------------|
| **Legislative Matters** | Legistar Web API | Recent council actions, ordinances, resolutions with status tracking |
| **Civics Statistics** | Legistar Web API | Matters introduced, adopted, failed/withdrawn counts |
| **Projects In-Process** | Legistar (computed) | Capital/development projects not yet adopted or failed |
| **Mill Rate** | CT Open Data | Current property tax mill rate and fiscal year |
| **City Calendar** | cityofnewhaven.com | Upcoming city meetings and events via calendar JSON |
| **Boards & Commissions** | Legistar Events API | Scheduled public meetings with body, date, location, links |

### 📰 News & Community Feeds

| Feature | Source | Description |
|---------|--------|-------------|
| **Who Knew Blog** | InfoNewHaven.com RSS | Local interest stories and historical pieces |
| **Food & Drink** | InfoNewHaven.com RSS | Restaurant news, food events, culinary features |
| **Music & Arts** | InfoNewHaven.com RSS | Cultural events, concerts, art exhibitions |
| **IAFF Headlines** | Local 825 (scraped) | New Haven Fire Department union news |
| **Feed Aggregator** | Multiple sources | Unified, de-duplicated, date-sorted feed |
| **Category Filtering** | Client-side | Filter by News, Events, Weather, Civic, Arts, Community, Fire/Safety, Food |

### 📅 Events & Calendar

| Feature | Description |
|---------|-------------|
| **Weekly Calendar Grid** | 7-day view with event cards, navigable ±4 weeks |
| **Event Details Panel** | Title, time, location, source, summary, external link |
| **Stub Events Fallback** | Local community events when feeds are empty |
| **API Endpoint** | `/api/events/week?offset=N` for programmatic access |

### 🔗 Quick Actions (City Services)

| Category | Actions |
|----------|---------|
| **City Services** | Report Issue (SeeClickFix), 311/City Hall, Legistar, City Plan, Maps |
| **Resources** | City Jobs, Library (NHFPL), Parking, Trash & Recycling, Health Dept |
| **Emergency** | 911, Police Non-Emergency, Fire Non-Emergency, 211 United Way |

### 🗺️ Interactive Map

- **OpenStreetMap Embed** with New Haven centered
- **Layer Options**: General, Topographic, Cycle Routes, Public Transport
- **Configurable Coordinates** via environment variables

### 📱 Mobile Experience

| Feature | Description |
|---------|-------------|
| **Accordion Navigation** | Collapsible utility and map panels |
| **Day Pills** | Horizontal scrollable week navigator |
| **Event Cards** | Touch-friendly event browsing |
| **Bottom Sheet Details** | Slide-up event detail panel |
| **Responsive Grid** | Desktop 3-column → Mobile stacked layout |

### 🎨 User Experience

| Feature | Description |
|---------|-------------|
| **Dark Mode** | Toggle between light and dark themes; respects system preference |
| **Theme Persistence** | Saves preference to localStorage |
| **Auto Theme** | Automatically switches based on `prefers-color-scheme` |
| **Auto-Refresh** | Optional 5-minute auto-refresh with toggle |
| **Manual Refresh** | Refresh button with loading animation |
| **Filter Persistence** | Saves category filter preferences |
| **Keyboard Shortcuts** | `D` for dark mode, `R` for refresh, `Esc` to close panels |
| **Live Status Badge** | Visual indicator showing dashboard is receiving live data |
| **Data Freshness** | Timestamps showing when data was last updated |
| **Neighborhood Filter** | Focus on specific New Haven neighborhoods (Downtown, East Rock, Westville, etc.) |

### 🤖 Automatic Contextual Intelligence

| Feature | Description |
|---------|-------------|
| **Time-of-Day Greeting** | Personalized greeting based on morning/afternoon/evening/night |
| **Sunrise/Sunset Times** | Calculated daily sun times with day length |
| **Smart Tips** | Auto-generated advice based on weather, air quality, time, and day |
| **Holiday Detection** | Automatic recognition of federal holidays and observances |
| **Rush Hour Awareness** | Detects weekday rush hours and shows traffic tips |
| **Weather-Based Advice** | Contextual tips like "Bring an umbrella" or "Bundle up" |
| **Weekend Mode** | Different suggestions for weekends vs weekdays |

### 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/feeds` | GET | Aggregated feed items (optional `?category=` filter) |
| `/feeds/raw` | GET | Full aggregate (debugging) |
| `/feeds/view` | GET | Minimal Tailwind-powered feed browser |
| `/api/nws/alerts` | GET | NWS alerts (optional `?zone=`) |
| `/api/nws/forecast` | GET | NWS forecast (optional `?lat=&lon=`) |
| `/api/tides` | GET | Tide predictions (optional `?station=&date=`) |
| `/api/events/week` | GET | Weekly events (optional `?offset=`) |
| `/about` | GET | About page |

### ⚙️ Technical Features

- **TTL Caching**: 10-minute cache for feeds, 15-minute for weather
- **Auto Port Selection**: Finds available port if preferred is occupied
- **Environment Configuration**: Fully configurable via `.env`
- **Graceful Degradation**: Fallback content when feeds are unavailable
- **De-duplication**: Link-based de-duplication across feed sources

---

## 🚀 Suggested New Features

*Proposed enhancements to make Elm City Daily a truly dynamic, live-feed driven civic dashboard:*

### 🚌 Transportation & Mobility

| Feature | Source | Impact |
|---------|--------|--------|
| **CT Transit Bus Tracking** | CT Transit GTFS-RT | Real-time bus arrivals for key stops (Union Station, Green, Yale) |
| **Traffic Incidents** | CT DOT 511 Feed | Active road closures, accidents, construction |
| **Parking Availability** | City parking API | Real-time garage/lot capacity (Temple, Crown, Air Rights) |
| **Bike Share Status** | Bike New Haven / GBFS | Station availability and bike counts |
| **Metro-North Schedule** | MTA GTFS | Shore Line East train status to NYC/Stamford |

### 🏗️ Development & Planning

| Feature | Source | Impact |
|---------|--------|--------|
| **Active Building Permits** | Municity/City Plan | New construction, renovations, demolitions |
| **Zoning Board Agenda** | Legistar/City Plan | Upcoming zoning appeals and variances |
| **Development Pipeline** | City Plan Dept | Major projects tracker (Long Wharf, Science Park, etc.) |
| **Housing Permits** | CT DECD | Monthly housing starts and completions |

### 🚨 Public Safety

| Feature | Source | Impact |
|---------|--------|--------|
| **Police Blotter** | NHPD (if available) | Recent incident summaries (non-identifying) |
| **Fire Department Calls** | IAFF/NHFD | Active incidents and apparatus deployment |
| **Emergency Alerts** | Everbridge/CT Alerts | City-wide emergency notifications |
| **Road Closures** | City Public Works | Planned closures for events, construction |

### 🏥 Health & Human Services

| Feature | Source | Impact |
|---------|--------|--------|
| ~~**Air Quality Index**~~ | ~~EPA AirNow API~~ | ✅ **IMPLEMENTED** — See Weather & Environment |
| **COVID-19 Dashboard** | CT DPH (if active) | Case counts, vaccination data |
| **Food Pantry Hours** | Community partners | Food distribution schedules |
| **Warming/Cooling Centers** | City emergency mgmt | Extreme weather shelter locations |

### 💼 Economy & Employment

| Feature | Source | Impact |
|---------|--------|--------|
| **City Job Postings** | City HR/Legistar | Current municipal employment opportunities |
| **Business License Filings** | City Clerk | New business registrations and closures |
| **Unemployment Rate** | CT DOL | Monthly local unemployment statistics |
| **Commercial Vacancy** | Economic Development | Downtown/neighborhood vacancy tracking |

### 🎓 Education

| Feature | Source | Impact |
|---------|--------|--------|
| **NHPS Calendar** | New Haven Public Schools | School closures, delays, events |
| **School Board Meetings** | BOE Legistar | Upcoming board meetings and agendas |
| **Library Events** | NHFPL | New Haven Free Public Library programming |

### 🌳 Parks & Environment

| Feature | Source | Impact |
|---------|--------|--------|
| **Park Events** | Parks & Rec | Scheduled activities at city parks |
| **Beach Status** | Health Dept | Swimming advisories (Lighthouse Point, etc.) |
| **Tree Plantings** | Urban Resources | Tree planting schedule and locations |
| **Recycling Schedule** | Public Works | Neighborhood pickup calendars |

### 🗳️ Democracy & Engagement

| Feature | Source | Impact |
|---------|--------|--------|
| **Voter Registration Deadlines** | CT SOTS | Upcoming election registration cutoffs |
| **Polling Location Finder** | CT SOTS | Lookup by address |
| **Aldermanic Districts** | Board of Alders | Ward boundaries and representatives |
| **Public Comment Queue** | Legistar | Upcoming public hearing opportunities |
| **SeeClickFix Integration** | SeeClickFix API | Report issues, view nearby requests |

### 📡 Live Data Enhancements

| Feature | Description |
|---------|-------------|
| **WebSocket Updates** | Push notifications for breaking alerts |
| **Auto-Refresh** | Configurable polling intervals per data type |
| **Data Freshness Indicators** | "Updated 5 minutes ago" timestamps |
| **Offline Mode** | Service Worker caching for basic functionality |
| **RSS Feed Output** | `/feeds.rss` for feed reader subscriptions |

### 🎨 User Experience (Suggested)

| Feature | Description |
|---------|-------------|
| ~~**Dark Mode**~~ | ✅ **IMPLEMENTED** — Toggle + system preference support |
| **Customizable Layout** | Drag-and-drop panel arrangement |
| ~~**Saved Preferences**~~ | ✅ **IMPLEMENTED** — Theme saved to LocalStorage |
| **Neighborhood Picker** | Focus data on specific neighborhoods |
| **Accessibility Audit** | WCAG 2.1 AA compliance review |
| **Print Stylesheet** | Clean single-page printout for bulletin boards |

### 📊 Analytics & Visualization

| Feature | Description |
|---------|-------------|
| **Historical Charts** | Mill rate trends, crime stats, permits over time |
| **Comparative Dashboards** | New Haven vs. CT averages |
| **Heat Maps** | Geographic distribution of permits, incidents |
| **Budget Visualization** | City budget treemap or sunburst |

---

## 🛠️ Installation

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
# Clone and enter directory
git clone <repo-url> elm-city-daily
cd elm-city-daily

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the app
python app.py --port 5000
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | Elm City Daily | Dashboard title |
| `FEED_URLS` | (CT Mirror) | Comma-separated RSS feed URLs |
| `RSS_PER_FEED_LIMIT` | 5 | Items per feed |
| `RSS_OVERALL_LIMIT` | 20 | Total items cap |
| `WEATHER_LAT` | 41.3083 | Latitude for weather |
| `WEATHER_LON` | -72.9279 | Longitude for weather |
| `REQUEST_TIMEOUT` | 5 | HTTP timeout (seconds) |
| `LEGISTAR_BASE` | webapi.legistar.com/v1/newhaven | Legistar API base |
| `LEGISTAR_UI_HOST` | newhavenct.legistar.com | Legistar public UI |
| `TAX_RATE_URL` | (none) | CT Open Data tax dataset URL |
| `CITY_CALENDAR_JSON` | cityofnewhaven.com/civicax/citycalendar/calendarjson | City calendar endpoint |
| `AIRNOW_API_KEY` | (none) | EPA AirNow API key (free at https://docs.airnowapi.org/) |

---

## 📁 Project Structure

```
elm-city-daily/
├── app.py                 # Flask application factory and routes
├── config.py              # Configuration from environment
├── requirements.txt       # Python dependencies
├── refresh_feeds.py       # Cron script to pre-warm cache
├── feeds/
│   ├── aggregator.py      # Feed aggregation logic
│   ├── feed_parser.py     # RSS/iCal parsing
│   ├── iaff_scraper.py    # IAFF headlines scraper
│   └── sources.py         # Feed URL definitions
├── services/
│   ├── air_quality.py     # EPA AirNow API
│   ├── civics.py          # Legistar, tax rates, city calendar
│   ├── context.py         # Contextual intelligence (tips, greetings, sun times)
│   ├── events.py          # Stub event generator
│   ├── nws.py             # National Weather Service
│   ├── rss.py             # Generic RSS fetching
│   ├── tides.py           # NOAA tides
│   └── weather.py         # Open-Meteo weather
├── modules/
│   └── change_new_haven_live/  # City homepage scraper
├── templates/
│   ├── base.html          # Base template
│   ├── index.html         # Main dashboard
│   ├── feeds.html         # Feed browser
│   └── about.html         # About page
├── static/
│   ├── css/
│   │   ├── main.css       # Primary styles
│   │   └── mobile-nav.css # Mobile navigation
│   └── js/
│       ├── dashboard.js   # Dashboard interactivity
│       ├── clock.js       # Live clock
│       └── mobile-nav.js  # Mobile navigation
└── utils/
    └── cache.py           # TTL cache implementation
```

---

## 🔄 Data Sources & Attribution

### Primary Sources (Active)

| Source | Data | License/Terms |
|--------|------|---------------|
| [InfoNewHaven.com](https://www.infonewhaven.com) | RSS Feeds | Editorial use |
| [Legistar](https://webapi.legistar.com) | Legislative data | Public API |
| [Open-Meteo](https://open-meteo.com) | Weather | CC BY 4.0 |
| [NWS](https://www.weather.gov) | Forecasts/Alerts | Public domain |
| [NOAA CO-OPS](https://tidesandcurrents.noaa.gov) | Tides | Public domain |
| [EPA AirNow](https://www.airnow.gov) | Air Quality | Public API (free key) |
| [CT Open Data](https://data.ct.gov) | Tax rates | Public data |
| [City of New Haven](https://cityofnewhaven.com) | Calendar | Public data |
| [IAFF Local 825](https://newhavenfire.org) | Headlines | Public posting |

### Disabled Sources

| Source | Reason |
|--------|--------|
| City of New Haven RSS | Returns 403 Forbidden |
| InfoNewHaven iCal | Blocked by Sucuri JS challenge |

---

## 🤝 Contributing

This project aims to serve New Haven residents with accurate, timely civic information. Contributions are welcome, especially:

- New data source integrations
- Accessibility improvements
- Mobile experience enhancements
- Performance optimizations
- Documentation improvements

---

## 📜 License

This project is open source and available for civic use. Data sources retain their respective licenses and terms of service.

---

## 🌳 About the Name

New Haven is known as "The Elm City" for its historic elm trees that once lined the streets, planted in the 1780s. Though Dutch elm disease devastated the original canopy, the name endures as a symbol of civic pride and resilience.

---

*Built with ❤️ for New Haven by public servants who believe in transparent, accessible civic information.*
