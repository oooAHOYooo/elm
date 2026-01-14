# 🚀 Run Roadie Locally - Step by Step

## Quick Start (5 minutes if you have everything installed)

### 1. Install PostgreSQL with PostGIS

**Windows:**
- Download [PostgreSQL with PostGIS](https://postgis.net/windows_downloads/)
- Install it (includes PostGIS automatically)
- Start PostgreSQL service

**macOS:**
```bash
brew install postgresql postgis
brew services start postgresql
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib postgis
sudo systemctl start postgresql
```

### 2. Create Database

Open terminal and run:
```bash
psql postgres
```

Then in psql:
```sql
CREATE DATABASE roadie;
CREATE USER roadie_user WITH PASSWORD 'roadie123';
GRANT ALL PRIVILEGES ON DATABASE roadie TO roadie_user;
\c roadie
CREATE EXTENSION postgis;
\q
```

### 3. Start Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt

# Create .env file
# Windows:
copy env.example .env
# macOS/Linux:
cp env.example .env

# Edit .env file - change this line:
# DATABASE_URL=postgresql://roadie_user:roadie123@localhost:5432/roadie

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

✅ Backend running on **http://localhost:8000**

### 4. Start Frontend (New Terminal)

```bash
cd frontend

# Install packages
npm install

# Create .env.local file
# Windows:
copy .env.example .env.local
# macOS/Linux:
cp .env.example .env.local

# .env.local should have:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

✅ Frontend running on **http://localhost:3000**

### 5. Open in Browser

Go to **http://localhost:3000** and sign up!

---

## 📝 What You Need

- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ ([Download](https://nodejs.org/))
- PostgreSQL 15+ with PostGIS (see above)

---

## 🐛 Common Issues

**"Can't connect to database"**
- Make sure PostgreSQL is running
- Check `DATABASE_URL` in backend/.env matches your setup
- Verify database exists: `psql -l | grep roadie`

**"Port already in use"**
- Backend uses port 8000
- Frontend uses port 3000
- Kill processes using these ports or change them

**"Module not found"**
- Make sure virtual environment is activated (backend)
- Run `pip install -r requirements.txt` again
- Run `npm install` again (frontend)

**"PostGIS extension error"**
- Make sure you ran `CREATE EXTENSION postgis;` in the database
- Check: `psql roadie -c "SELECT PostGIS_version();"`

---

## ✅ Verify It's Working

1. Backend: Visit http://localhost:8000/health (should show `{"status": "healthy"}`)
2. Frontend: Visit http://localhost:3000 (should show login page)
3. Register a new account
4. Login and see dashboard!

---

## 🎯 Next Steps

- Record a drive (use mobile app)
- View drives on web dashboard
- Customize the dark glass theme!

For more details, see [LOCAL_SETUP.md](./LOCAL_SETUP.md)

