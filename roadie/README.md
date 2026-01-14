# Roadie - Driving Journal App 🚗

A Strava-like app for tracking your drives. Record your journeys, visualize your routes, and maintain a digital journal of your automotive adventures.

## 🏗️ Project Structure

```
roadie/
├── backend/          # FastAPI backend
├── frontend/         # Next.js web app
├── mobile/           # React Native + Expo app
└── docs/             # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS extension
- Expo CLI (`npm install -g expo-cli`)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your API URL
npm run dev
```

### Mobile Setup
```bash
cd mobile
npm install
cp .env.example .env
# Edit .env with your API URL
npx expo start
```

## 🌐 Deployment

### Backend (Render)
1. Connect your GitHub repo to Render
2. Create a new Web Service
3. Set build command: `cd backend && pip install -r requirements.txt`
4. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL database with PostGIS extension
6. Set environment variables

### Frontend (Vercel)
1. Connect your GitHub repo to Vercel
2. Set root directory to `frontend`
3. Add environment variables
4. Deploy!

## 📱 Features

- ✅ Record drives with GPS tracking
- ✅ View drive history with interactive maps
- ✅ Statistics dashboard
- ✅ User authentication
- ✅ Cross-platform (iOS, Android, Web)

## 🛠️ Tech Stack

- **Backend**: Python + FastAPI + PostgreSQL + PostGIS
- **Frontend**: Next.js + React + Leaflet
- **Mobile**: React Native + Expo
- **Maps**: OpenStreetMap + Leaflet

## 📄 License

MIT

