# 🚀 Quick Start Guide

## Before Running `python app.py`

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Or if using a virtual environment:
```bash
# Create venv (first time only)
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment File (Optional)

The app will work without a `.env` file (it uses defaults), but you can create one for customization:

```bash
# Copy the example
copy .env.example .env

# Edit .env to add your AirNow API key (optional but recommended for AQI)
# Get a free key at: https://docs.airnowapi.org/
```

### 3. Run the App

**Option A: Direct run**
```bash
python app.py
```

**Option B: With debug mode**
```bash
python app.py --debug
```

**Option C: Use the dev launcher**
```bash
python run_dev.py
```

### 4. Access the App

Open your browser to:
- **http://127.0.0.1:5000** (local)
- **http://localhost:5000** (alternative)

## What to Expect

✅ The app should start and show:
- Weather dashboard
- Events calendar
- Quick links with popups
- News feeds

⚠️ If some APIs fail (weather, AQI, etc.), the app will still work but show "Loading..." or fallback content.

## Troubleshooting

**"Python was not found"**
- Try `py app.py` instead of `python app.py`
- Or use the full path: `C:\Python3x\python.exe app.py`
- Or activate your virtual environment first

**Import errors**
- Run: `pip install -r requirements.txt`
- Make sure you're in the project directory

**Port already in use**
- Try: `python app.py --port 5001`
- Or kill the process using port 5000

**Missing .env file**
- Not required! The app uses sensible defaults
- Only create one if you want to customize settings

## Default Configuration

The app works out-of-the-box with these defaults:
- Location: New Haven, CT (41.3083, -72.9279)
- RSS Feed: CT Mirror
- Port: 5000
- Air Quality: Works without API key (but better with one)

---

**Ready to go!** Just install dependencies and run `python app.py` 🎉
