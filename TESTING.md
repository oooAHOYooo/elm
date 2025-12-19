# Testing Elm City Daily

## Quick Start

### 1. Start the Development Server

**Option A: Use the dev launcher script**
```bash
python run_dev.py
```

**Option B: Run directly**
```bash
python app.py --debug
```

The server will start at `http://127.0.0.1:5000`

### 2. Run the Test Suite

In a **separate terminal**, run:
```bash
python test_app.py
```

This will test all endpoints:
- ✅ Homepage
- ✅ About page
- ✅ Feeds API (JSON)
- ✅ RSS Feed
- ✅ NWS Alerts API
- ✅ Tides API
- ✅ Events Week API

## Manual Testing

### Test in Browser

1. **Homepage**: http://127.0.0.1:5000
   - Check weather, events, quick links
   - Test dark mode toggle
   - Test week navigation
   - Click quick links to see popups

2. **RSS Feed**: http://127.0.0.1:5000/feeds.rss
   - Should show XML RSS feed
   - Can subscribe in feed readers

3. **API Endpoints**:
   - http://127.0.0.1:5000/feeds (JSON)
   - http://127.0.0.1:5000/api/nws/alerts
   - http://127.0.0.1:5000/api/tides
   - http://127.0.0.1:5000/api/events/week

### Test Print Stylesheet

1. Open homepage in browser
2. Press `Ctrl+P` (or Cmd+P on Mac)
3. Should see clean "fridge card" layout
4. Calendar should be optimized for printing

## Troubleshooting

**Server won't start?**
- Check if port 5000 is in use: `netstat -ano | findstr :5000`
- Try a different port: `python app.py --port 5001`

**Tests fail?**
- Make sure the server is running first
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists (copy from `.env.example` if needed)

**Import errors?**
- Activate virtual environment: `.venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
