# Deployment Guide - Roadie

This guide covers deploying Roadie to Render (backend) and Vercel (frontend).

## 🎯 Why Render + Vercel?

- **Render**: Excellent for Python/FastAPI backends, includes PostgreSQL with PostGIS, easy setup
- **Vercel**: Perfect for Next.js, automatic deployments, global CDN, free tier

---

## 📦 Prerequisites

1. GitHub account
2. Render account (sign up at [render.com](https://render.com))
3. Vercel account (sign up at [vercel.com](https://vercel.com))
4. Push your code to a GitHub repository

---

## 🗄️ Step 1: Deploy Database (Render)

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `roadie-db`
   - **Database**: `roadie`
   - **User**: `roadie_user`
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15
4. Click **"Create Database"**
5. **Important**: After creation, go to database settings and enable **PostGIS extension**:
   - Go to database → **"Shell"** tab
   - Run: `CREATE EXTENSION postgis;`
6. Copy the **Internal Database URL** (you'll need this)

---

## 🔧 Step 2: Deploy Backend (Render)

### Option A: Using render.yaml (Recommended)

1. In your GitHub repo, make sure `backend/render.yaml` exists
2. Go to Render Dashboard → **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create services automatically
5. Update environment variables:
   - `CORS_ORIGINS`: Your Vercel frontend URL (e.g., `https://roadie.vercel.app`)

### Option B: Manual Setup

1. Go to Render Dashboard → **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `roadie-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   ```
   DATABASE_URL=<your-postgres-internal-url>
   SECRET_KEY=<generate-a-random-secret-key>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=https://your-frontend.vercel.app
   ENVIRONMENT=production
   ```
5. Click **"Create Web Service"**
6. After deployment, run migrations:
   - Go to service → **"Shell"** tab
   - Run: `cd backend && alembic upgrade head`

---

## 🌐 Step 3: Deploy Frontend (Vercel)

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
   ```
6. Click **"Deploy"**

---

## 📱 Step 4: Update Mobile App Configuration

1. Update `mobile/.env`:
   ```
   EXPO_PUBLIC_API_URL=https://your-backend.onrender.com
   ```
2. For production builds:
   ```bash
   cd mobile
   npx expo build:android
   npx expo build:ios
   ```

---

## ✅ Step 5: Verify Deployment

1. **Backend Health Check**:
   - Visit: `https://your-backend.onrender.com/health`
   - Should return: `{"status": "healthy"}`

2. **Frontend**:
   - Visit your Vercel URL
   - Should show login page

3. **Test Flow**:
   - Register a new user
   - Create a test drive
   - View drive on map

---

## 🔐 Environment Variables Reference

### Backend (Render)
```env
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
```

### Mobile
```env
EXPO_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## 🚀 Post-Deployment

### Enable PostGIS Extension
After database is created, run in Render database shell:
```sql
CREATE EXTENSION postgis;
```

### Run Migrations
In Render backend shell:
```bash
cd backend
alembic upgrade head
```

### Update CORS
Make sure `CORS_ORIGINS` in backend includes your Vercel frontend URL.

---

## 🐛 Troubleshooting

### Backend Issues

**Database connection errors:**
- Check `DATABASE_URL` is correct
- Use **Internal Database URL** from Render (not external)
- Verify PostGIS extension is enabled

**CORS errors:**
- Update `CORS_ORIGINS` to include your frontend URL
- Restart backend service

**Migration errors:**
- Run `alembic upgrade head` in Render shell
- Check database has PostGIS extension

### Frontend Issues

**API connection errors:**
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is running and accessible
- Verify CORS is configured correctly

**Build errors:**
- Check Node.js version (should be 18+)
- Clear `.next` folder and rebuild

### Mobile Issues

**Location permissions:**
- iOS: Check `Info.plist` has location permissions
- Android: Check `AndroidManifest.xml` has permissions

**API errors:**
- Verify `EXPO_PUBLIC_API_URL` is set correctly
- Check backend CORS includes mobile app origin

---

## 📊 Monitoring

### Render
- View logs in Render dashboard
- Set up alerts for service downtime
- Monitor database usage

### Vercel
- View deployment logs
- Monitor analytics
- Set up error tracking (Sentry recommended)

---

## 💰 Cost Estimate

### Free Tier (MVP)
- **Render**: Free tier available (limited hours)
- **Vercel**: Free tier (unlimited)
- **PostgreSQL**: Free tier (limited storage)

### Production (Recommended)
- **Render Backend**: ~$7/month
- **Render PostgreSQL**: ~$7/month
- **Vercel**: Free (or Pro $20/month for team features)

**Total: ~$14/month** for production deployment

---

## 🔄 Continuous Deployment

Both Render and Vercel automatically deploy on git push to main branch.

**Workflow:**
1. Push code to GitHub
2. Render rebuilds backend
3. Vercel rebuilds frontend
4. Both deploy automatically

---

## ✅ Checklist

- [ ] Database created on Render with PostGIS
- [ ] Backend deployed on Render
- [ ] Environment variables set
- [ ] Migrations run
- [ ] Frontend deployed on Vercel
- [ ] CORS configured correctly
- [ ] Health check passes
- [ ] Test user registration
- [ ] Test drive creation
- [ ] Test map visualization

---

## 🎉 You're Done!

Your Roadie app should now be live! Share your Vercel URL with users.

**Next Steps:**
- Set up custom domain (optional)
- Configure error tracking (Sentry)
- Set up analytics
- Enable background location tracking for mobile

