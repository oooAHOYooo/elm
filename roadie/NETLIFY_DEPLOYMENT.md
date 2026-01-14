# 🚀 Deploy Roadie to Netlify (Frontend) + Render (Backend)

## ⚠️ Important: You Need TWO Platforms

- **Frontend (Next.js)** → **Netlify** ✅ (Works, but Vercel is better)
- **Backend (FastAPI/Python)** → **Render** ✅ (Required - Netlify can't run Python backends)

**Why not all on Netlify?**
- Netlify doesn't support Python/FastAPI backends
- Netlify Functions are for small serverless functions, not full APIs
- You'd need to rewrite the entire backend (not worth it)

---

## ✅ Quick Answer: Yes, You Can Use Netlify!

**For MVP/Quick Setup:**
- ✅ Frontend on Netlify - **Works fine** (just needs config)
- ✅ Backend on Render - **Required anyway**
- ⚠️ Vercel is better for Next.js, but Netlify works

**Time Comparison:**
- Netlify setup: ~10 minutes
- Vercel setup: ~5 minutes (easier, but you already know Netlify)

---

## 🚀 Quick Deployment Guide

### Step 1: Deploy Backend to Render (Required)

1. Go to [render.com](https://render.com) → Sign up
2. **New +** → **PostgreSQL** → Create database
3. **New +** → **Web Service** → Connect GitHub repo
4. Configure:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see DEPLOYMENT.md)
6. Copy your Render backend URL (e.g., `https://roadie-api.onrender.com`)

### Step 2: Deploy Frontend to Netlify

1. Go to [netlify.com](https://netlify.com) → Sign in
2. **Add new site** → **Import an existing project**
3. Connect your GitHub repository
4. Configure build settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/.next`
5. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://roadie-api.onrender.com
   NEXT_PUBLIC_MAP_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
   ```
6. Click **Deploy site**

### Step 3: Update Backend CORS

1. Go back to Render dashboard
2. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://your-site.netlify.app
   ```
3. Restart backend service

---

## 📝 Netlify Configuration File

Create `netlify.toml` in your project root:

```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "frontend/.next"

[[plugins]]
  package = "@netlify/plugin-nextjs"

[build.environment]
  NODE_VERSION = "18"
```

Or create `frontend/netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

---

## ⚡ Netlify vs Vercel for Next.js

| Feature | Netlify | Vercel |
|---------|---------|--------|
| **Next.js Support** | ✅ Good | ✅ Excellent (made by Next.js creators) |
| **Setup Time** | ~10 min | ~5 min |
| **Auto Deploy** | ✅ Yes | ✅ Yes |
| **Performance** | ✅ Good | ✅ Excellent |
| **Free Tier** | ✅ Generous | ✅ Generous |
| **Ease of Use** | ✅ Easy | ✅ Very Easy |
| **Your Experience** | ✅ You already know it | ⚠️ New platform |

**Verdict:** For MVP, Netlify is fine! Vercel is slightly better, but not worth switching if you're short on time.

---

## 🎯 Recommendation

**If you're short on time:**
1. ✅ Use Netlify for frontend (you already know it)
2. ✅ Use Render for backend (required anyway)
3. ✅ Get it deployed in 15 minutes
4. ⏭️ Switch to Vercel later if you want (easy migration)

**Why this works:**
- Netlify handles Next.js well
- You're already familiar with Netlify
- Backend must be on Render anyway (can't use Netlify)
- You can always migrate frontend to Vercel later (takes 5 minutes)

---

## 🚨 Important Notes

1. **Next.js on Netlify needs plugin:**
   - Install: `npm install --save-dev @netlify/plugin-nextjs`
   - Or use the `netlify.toml` config above

2. **Build settings matter:**
   - Base directory: `frontend`
   - Publish directory: `frontend/.next` (or `.next` if base is frontend)

3. **Environment variables:**
   - Must be set in Netlify dashboard
   - Use `NEXT_PUBLIC_` prefix for client-side vars

4. **Backend still on Render:**
   - This is non-negotiable
   - Netlify can't run Python/FastAPI
   - Render is free tier anyway

---

## ✅ Quick Checklist

- [ ] Backend deployed to Render
- [ ] Frontend deployed to Netlify
- [ ] Environment variables set in Netlify
- [ ] CORS updated in Render backend
- [ ] Test registration/login
- [ ] Test drive creation/viewing

---

## 🎉 Bottom Line

**Yes, use Netlify!** It works fine for Next.js, and since you already know it, you'll save time. The backend must go on Render anyway, so you're not losing anything by using Netlify for the frontend.

**Time to deploy:** ~15 minutes total
- Backend (Render): 10 min
- Frontend (Netlify): 5 min

Go for it! 🚀

