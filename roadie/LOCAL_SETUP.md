# 🚀 Run Roadie Locally - Quick Guide

Get Roadie running on your machine in 15 minutes!

## ✅ Prerequisites

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 15+** with PostGIS - See below
- **Git** (optional, if cloning)

## 📦 Step 1: Install PostgreSQL with PostGIS

### macOS
```bash
brew install postgresql postgis
brew services start postgresql
```

### Windows
1. Download [PostgreSQL with PostGIS](https://postgis.net/install/)
2. Install with PostGIS extension included
3. Start PostgreSQL service

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis
sudo systemctl start postgresql
```

## 🗄️ Step 2: Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE roadie;
CREATE USER roadie_user WITH PASSWORD 'roadie123';
GRANT ALL PRIVILEGES ON DATABASE roadie TO roadie_user;

# Connect to roadie database
\c roadie

# Enable PostGIS extension
CREATE EXTENSION postgis;

# Exit
\q
```

## 🔧 Step 3: Setup Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env file (use your favorite editor)
# Update DATABASE_URL:
# DATABASE_URL=postgresql://roadie_user:roadie123@localhost:5432/roadie
```

**Edit `.env` file:**
```env
DATABASE_URL=postgresql://roadie_user:roadie123@localhost:5432/roadie
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:3000,http://localhost:8081
ENVIRONMENT=development
```

```bash
# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload
```

Backend will run on **http://localhost:8000** ✅

## 🌐 Step 4: Setup Frontend

Open a **new terminal** (keep backend running):

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local (already configured for localhost)
```

**`.env.local` should have:**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

```bash
# Start frontend
npm run dev
```

Frontend will run on **http://localhost:3000** ✅

## 📱 Step 5: Setup Mobile (Optional)

Open a **new terminal**:

```bash
# Navigate to mobile
cd mobile

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env
```

**`.env` should have:**
```env
EXPO_PUBLIC_API_URL=http://localhost:8000
```

**For iOS Simulator:**
```bash
npx expo start --ios
```

**For Android Emulator:**
```bash
npx expo start --android
```

**For Physical Device:**
1. Find your computer's IP address:
   - macOS/Linux: `ifconfig | grep "inet "`
   - Windows: `ipconfig`
2. Update `.env`: `EXPO_PUBLIC_API_URL=http://YOUR_IP:8000`
3. Run: `npx expo start`
4. Scan QR code with Expo Go app

## ✅ Step 6: Test It!

1. Open **http://localhost:3000** in your browser
2. Click **"Sign up"**
3. Create an account
4. You should see the dashboard!

## 🐛 Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Verify database exists: `psql -l | grep roadie`
- Check `.env` file has correct `DATABASE_URL`
- Make sure virtual environment is activated

### Database connection errors
- Verify PostgreSQL is running
- Check username/password in `DATABASE_URL`
- Ensure PostGIS extension is enabled: `psql roadie -c "SELECT PostGIS_version();"`

### Frontend can't connect to backend
- Make sure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Open browser console for errors
- Try: `curl http://localhost:8000/health`

### Mobile can't connect
- For simulator: Use `http://localhost:8000`
- For physical device: Use your computer's IP address
- Make sure backend is accessible from your network
- Check firewall settings

## 🎉 You're Running Locally!

Now you can:
- ✅ Test all features
- ✅ Make code changes
- ✅ See changes instantly (hot reload)
- ✅ Debug easily

**Next Steps:**
- Record a test drive (mobile app)
- View it on the web dashboard
- Customize the UI
- Add new features!

## 📝 Quick Commands Reference

```bash
# Backend
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev

# Mobile
cd mobile
npx expo start
```

## 🔥 Pro Tips

1. **Keep terminals open** - You need all 3 running (backend, frontend, mobile)
2. **Check ports** - Make sure 8000 and 3000 aren't in use
3. **Database first** - Always start PostgreSQL before backend
4. **Hot reload** - Both frontend and backend auto-reload on changes!

Enjoy your dark glass-themed Roadie app! 🚗✨

