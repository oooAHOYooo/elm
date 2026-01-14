# 🚀 Quick Deployment Guide - Roadie

## ⚠️ Important: You Need TWO Platforms

- **Frontend (Next.js)** → **Vercel** ✅ (Perfect for Next.js)
- **Backend (FastAPI/Python)** → **Render** ✅ (Perfect for Python)
- **Database (PostgreSQL)** → **Render** ✅ (Included with Render)

**Why not all on Vercel?** Vercel is amazing for Next.js frontends, but doesn't support Python backends well. Render is better for Python/FastAPI.

---

## 📋 Step-by-Step Deployment

### Step 1: Push Code to GitHub

```bash
# If you haven't already
git init
git add .
git commit -m "Initial commit - Roadie MVP"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy Database (Render) - 5 minutes

1. Go to [render.com](https://render.com) and sign up/login
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `roadie-db`
   - **Database**: `roadie`
   - **User**: `roadie_user`
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15
4. Click **"Create Database"**
5. **IMPORTANT**: After creation:
   - Go to your database → **"Shell"** tab
   - Run: `CREATE EXTENSION postgis;`
6. Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3: Deploy Backend (Render) - 10 minutes

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `roadie-api`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   ```
   DATABASE_URL=<paste-internal-database-url-from-step-2>
   SECRET_KEY=<generate-random-string-here>
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=7
   CORS_ORIGINS=https://your-frontend.vercel.app
   ENVIRONMENT=production
   ```
   **Note**: For `CORS_ORIGINS`, you'll update this after deploying frontend
   **Note**: For `SECRET_KEY`, generate a random string (you can use: `openssl rand -hex 32`)
5. Click **"Create Web Service"**
6. Wait for deployment (2-3 minutes)
7. After deployment, go to **"Shell"** tab and run:
   ```bash
   cd backend
   alembic upgrade head
   ```
8. Copy your backend URL (e.g., `https://roadie-api.onrender.com`)

### Step 4: Deploy Frontend (Vercel) - 5 minutes

1. Go to [vercel.com](https://vercel.com) and sign up/login
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
5. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://roadie-api.onrender.com
   NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
   ```
   (Use your actual Render backend URL from Step 3)
6. Click **"Deploy"**
7. Wait for deployment (1-2 minutes)
8. Copy your frontend URL (e.g., `https://roadie.vercel.app`)

### Step 5: Update Backend CORS - 2 minutes

1. Go back to Render dashboard → Your backend service
2. Go to **"Environment"** tab
3. Update `CORS_ORIGINS` to your Vercel URL:
   ```
   CORS_ORIGINS=https://roadie.vercel.app
   ```
4. Click **"Save Changes"**
5. Render will automatically redeploy

### Step 6: Test Everything - 5 minutes

1. Visit your Vercel frontend URL
2. Register a new account
3. Login
4. You should see the dashboard!

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Database created on Render with PostGIS enabled
- [ ] Backend deployed on Render
- [ ] Environment variables set in backend
- [ ] Migrations run (`alembic upgrade head`)
- [ ] Frontend deployed on Vercel
- [ ] Environment variables set in frontend
- [ ] CORS updated with frontend URL
- [ ] Tested registration and login

---

## 💰 Cost

### Free Tier (Perfect for MVP)
- **Render Backend**: Free (with limitations)
- **Render Database**: Free (limited storage)
- **Vercel Frontend**: Free (unlimited)

**Total: $0/month** for MVP! 🎉

### If You Need More (Later)
- **Render Backend**: ~$7/month
- **Render Database**: ~$7/month
- **Vercel**: Still free (or $20/month for team features)

---

## 🐛 Common Issues

### Backend won't start
- Check build logs in Render
- Verify `requirements.txt` is correct
- Make sure Python 3 is selected

### Database connection errors
- Use **Internal Database URL** (not external)
- Check PostGIS extension is enabled
- Verify `DATABASE_URL` environment variable

### CORS errors
- Make sure `CORS_ORIGINS` includes your Vercel URL
- Restart backend after updating CORS
- Check frontend `NEXT_PUBLIC_API_URL` is correct

### Frontend can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running (visit `/health` endpoint)
- Make sure CORS is configured

---

## 🎯 What to Do Right Now

1. **Push to GitHub** (if not done)
2. **Deploy Database** on Render (5 min)
3. **Deploy Backend** on Render (10 min)
4. **Deploy Frontend** on Vercel (5 min)
5. **Update CORS** (2 min)
6. **Test it!** 🎉

**Total time: ~25 minutes**

---

## 📱 Mobile App

For the mobile app, you'll need to:
1. Update `mobile/.env` with your Render backend URL
2. Build with Expo:
   ```bash
   cd mobile
   npx expo build:android
   npx expo build:ios
   ```

But for now, focus on getting web working first!

---

## 🎉 You're Ready!

Follow these steps and you'll have Roadie live in production. Start with Step 1 and work through them in order.

Need help? Check the full [DEPLOYMENT.md](./DEPLOYMENT.md) for more details.

