# 🚀 Deploy Roadie to Render (elmcitydaily.com)

Since your elm project is already on Render at **elmcitydaily.com**, here's how to add Roadie:

## 📋 Your Setup

- **Main elm app**: Python app at elmcitydaily.com (already deployed)
- **Roadie backend**: FastAPI (needs separate Render service)
- **Roadie frontend**: Next.js (can be on Render or Netlify/Vercel)

## 🎯 Option 1: Subdomain (Recommended)

**URL Structure:**
- Main app: `elmcitydaily.com` (your existing Python app)
- Roadie: `roadie.elmcitydaily.com` (new subdomain)

### Steps:

1. **Deploy Roadie Backend as New Service on Render:**
   - Go to Render dashboard
   - **New +** → **Web Service**
   - Connect your GitHub repo (elm project)
   - Configure:
     - **Root Directory**: `roadie/backend`
     - **Build**: `cd roadie/backend && pip install -r requirements.txt`
     - **Start**: `cd roadie/backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables (database, etc.)
   - Get the service URL (e.g., `roadie-api.onrender.com`)

2. **Deploy Roadie Frontend:**
   - **Option A**: Netlify/Vercel (easiest)
     - Deploy from `roadie/frontend` directory
     - Set `NEXT_PUBLIC_API_URL` to your Render backend URL
     - Use custom domain: `roadie.elmcitydaily.com`
   
   - **Option B**: Render Static Site
     - **New +** → **Static Site**
     - Root: `roadie/frontend`
     - Build: `cd roadie/frontend && npm run build`
     - Publish: `roadie/frontend/.next`
     - Custom domain: `roadie.elmcitydaily.com`

## 🎯 Option 2: Subfolder Path

**URL Structure:**
- Main app: `elmcitydaily.com`
- Roadie: `elmcitydaily.com/roadie`

This is trickier - you'd need to configure your main Python app to serve the Next.js app, or use a reverse proxy.

## 🎯 Option 3: Separate Domain

**URL Structure:**
- Main app: `elmcitydaily.com`
- Roadie: `roadie.elmcitydaily.com` or `getroadie.com`

Easiest - just deploy Roadie separately with its own domain.

## ✅ Recommended: Subdomain Setup

1. **Backend**: New Render service → `roadie-api.onrender.com`
2. **Frontend**: Netlify/Vercel → `roadie.elmcitydaily.com`
3. **Database**: Render PostgreSQL (shared or separate)

## 📝 Quick Deploy Commands

### Backend (Render):
```
Root: roadie/backend
Build: cd roadie/backend && pip install -r requirements.txt
Start: cd roadie/backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Netlify):
```
Base: roadie/frontend
Build: cd roadie/frontend && npm run build
Publish: roadie/frontend/.next
```

## 🔗 Your URLs Will Be:

- **Main app**: `elmcitydaily.com` (existing)
- **Roadie web**: `roadie.elmcitydaily.com` (new)
- **Roadie API**: `roadie-api.onrender.com` (new)

## 🚀 Next Steps:

1. Deploy Roadie backend to Render (new service)
2. Deploy Roadie frontend to Netlify/Vercel
3. Point `roadie.elmcitydaily.com` to frontend
4. Update CORS in backend to allow `roadie.elmcitydaily.com`


