# Roadie - Quick Start Guide

Get Roadie up and running locally in minutes!

## 🚀 Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS extension
- Git

## 📦 Step 1: Clone & Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd roadie

# Or if you already have it
cd roadie
```

## 🗄️ Step 2: Setup Database

### Install PostgreSQL with PostGIS

**macOS:**
```bash
brew install postgresql postgis
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib postgis
sudo systemctl start postgresql
```

**Windows:**
- Download from [postgresql.org](https://www.postgresql.org/download/windows/)
- Install PostGIS extension during installation

### Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE roadie;
CREATE USER roadie_user WITH PASSWORD 'your_password';
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
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://roadie_user:your_password@localhost:5432/roadie

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

## 🌐 Step 4: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start development server
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📱 Step 5: Setup Mobile (Optional)

```bash
cd mobile

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env
# EXPO_PUBLIC_API_URL=http://localhost:8000

# Start Expo
npx expo start
```

Scan QR code with Expo Go app on your phone.

## ✅ Step 6: Test It Out

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Login
4. On mobile: Start recording a drive
5. View your drives on the web dashboard

## 🐛 Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Ensure PostGIS extension is enabled

### Backend Issues
- Check Python version: `python --version` (should be 3.11+)
- Verify virtual environment is activated
- Check all dependencies installed: `pip list`

### Frontend Issues
- Clear `.next` folder: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 18+)

### Mobile Issues
- Make sure backend is running
- Check `EXPO_PUBLIC_API_URL` is correct
- For iOS simulator, use `http://localhost:8000`
- For physical device, use your computer's IP: `http://192.168.x.x:8000`

## 📚 Next Steps

- Read [DEPLOYMENT.md](./DEPLOYMENT.md) to deploy to production
- Check [PROJECT_PLAN.md](./PROJECT_PLAN.md) for feature roadmap
- Review [TECH_STACK.md](./TECH_STACK.md) for architecture details

## 🎉 You're Ready!

Your Roadie app is now running locally. Start tracking your drives! 🚗

