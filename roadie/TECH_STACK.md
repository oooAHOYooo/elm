# Carva - Recommended Tech Stack

## 🎯 Overview

This document details the recommended tech stack for building Carva, a cross-platform driving journal app. The stack is chosen for:
- **Code reusability** across platforms
- **Developer productivity** with modern tools
- **Scalability** for future growth
- **Cost efficiency** (open-source first)
- **Performance** for location tracking

---

## 📱 Mobile Apps (iOS & Android)

### **React Native with Expo**

**Why:**
- ✅ Write once, deploy to both iOS and Android
- ✅ Expo provides built-in location services, camera, file system
- ✅ Over-the-air updates without app store approval
- ✅ Easy development with Expo Go app
- ✅ Built-in build service (EAS Build)
- ✅ Great developer experience

**Key Packages:**
```json
{
  "expo": "~50.0.0",
  "expo-location": "^16.5.0",        // GPS tracking
  "expo-task-manager": "^11.0.0",    // Background tasks
  "react-native-maps": "^1.8.0",     // Map rendering
  "@react-navigation/native": "^6.1.0", // Navigation
  "@react-native-async-storage/async-storage": "^1.19.0", // Local storage
  "react-native-vector-icons": "^10.0.0", // Icons
  "axios": "^1.6.0"                  // API calls
}
```

**Alternatives Considered:**
- **Flutter**: Great performance, but requires learning Dart
- **Native (Swift/Kotlin)**: Best performance, but 2x development time
- **Ionic**: Web-based, less native feel

---

## 🌐 Web App

### **Next.js 14 (React Framework)**

**Why:**
- ✅ Server-side rendering (SSR) for better SEO
- ✅ API routes (can share backend logic)
- ✅ Excellent performance with automatic code splitting
- ✅ Great developer experience
- ✅ Easy deployment on Vercel
- ✅ Can share React components with mobile (with React Native Web)

**Key Packages:**
```json
{
  "next": "^14.0.0",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "leaflet": "^1.9.4",              // OpenStreetMap maps
  "react-leaflet": "^4.2.1",        // React wrapper for Leaflet
  "axios": "^1.6.0",                // API calls
  "zustand": "^4.4.0",              // State management (lightweight)
  "react-query": "^5.0.0",          // Data fetching & caching
  "tailwindcss": "^3.3.0",          // Styling
  "framer-motion": "^10.16.0"       // Animations
}
```

**Alternatives Considered:**
- **Remix**: Similar to Next.js, newer framework
- **Vite + React**: Faster dev, but no SSR out of box
- **SvelteKit**: Smaller bundle, but less ecosystem

---

## 🔧 Backend

### **Node.js with NestJS**

**Why:**
- ✅ TypeScript support out of the box
- ✅ Modular architecture (like Angular)
- ✅ Built-in dependency injection
- ✅ Great for building scalable APIs
- ✅ Excellent documentation
- ✅ Built-in validation, guards, interceptors

**Alternative: Express.js** (simpler, more flexible, but less structured)

**Key Packages:**
```json
{
  "@nestjs/core": "^10.0.0",
  "@nestjs/common": "^10.0.0",
  "@nestjs/platform-express": "^10.0.0",
  "@nestjs/typeorm": "^10.0.0",      // ORM
  "@nestjs/jwt": "^10.1.0",          // Authentication
  "@nestjs/passport": "^10.0.0",     // Auth strategies
  "typeorm": "^0.3.17",              // Database ORM
  "pg": "^8.11.0",                   // PostgreSQL driver
  "bcrypt": "^5.1.0",                // Password hashing
  "class-validator": "^0.14.0",     // DTO validation
  "class-transformer": "^0.5.1",    // DTO transformation
  "socket.io": "^4.5.0",             // WebSockets (real-time)
  "multer": "^1.4.5",                // File uploads
  "helmet": "^7.1.0",                // Security headers
  "compression": "^1.7.4"            // Response compression
}
```

**Runtime:** Node.js 18+ LTS

---

## 🗄️ Database

### **PostgreSQL 15+ with PostGIS Extension**

**Why:**
- ✅ Industry standard relational database
- ✅ PostGIS for geospatial queries (distance, routes, polygons)
- ✅ Excellent performance with proper indexing
- ✅ ACID compliance
- ✅ Free and open source
- ✅ Great tooling and ecosystem

**Key Features:**
- Spatial data types (POINT, LINESTRING, POLYGON)
- Spatial indexes (GIST)
- Geospatial functions (ST_Distance, ST_Within, etc.)

**ORM: TypeORM**
- TypeScript-first
- Great migration system
- Supports PostGIS types
- Active Record and Data Mapper patterns

**Example Query:**
```sql
-- Find drives within 10km of a point
SELECT * FROM drives 
WHERE ST_DWithin(
  start_location, 
  ST_MakePoint(-122.4194, 37.7749), 
  10000
);
```

**Alternatives Considered:**
- **MongoDB**: Good for flexible schemas, but PostGIS is better for geospatial
- **MySQL**: Doesn't have PostGIS equivalent
- **TimescaleDB**: Great for time-series, but overkill for MVP

---

## 🗺️ Maps & Geospatial

### **Primary: OpenStreetMap + Leaflet**

**Web:**
- **Leaflet.js** - Lightweight, open-source mapping library
- **React-Leaflet** - React components for Leaflet
- **Tile Server**: Use public OSM tiles or self-host with TileServer GL

**Mobile:**
- **react-native-maps** - Cross-platform map component
- **OpenStreetMap provider** - Free tiles

**Why OpenStreetMap:**
- ✅ Completely free
- ✅ No API keys required
- ✅ Open source
- ✅ Good coverage worldwide
- ✅ Customizable styling

**Package:**
```json
{
  "leaflet": "^1.9.4",
  "react-leaflet": "^4.2.1",
  "react-native-maps": "^1.8.0"
}
```

### **Alternative: Mapbox**

**Pros:**
- Better performance
- Beautiful default styling
- 50,000 free map loads/month
- Better mobile SDK

**Cons:**
- Requires API key
- Costs after free tier ($0.50 per 1,000 loads)
- Less "open source" feel

**When to use:** If you need better performance or styling and have budget

---

## 🔐 Authentication

### **JWT (JSON Web Tokens)**

**Implementation:**
- Access tokens (short-lived, 15 minutes)
- Refresh tokens (long-lived, 7 days)
- Stored in httpOnly cookies (web) or secure storage (mobile)

**Packages:**
- `@nestjs/jwt` - JWT handling
- `@nestjs/passport` - Authentication strategies
- `passport-jwt` - JWT strategy
- `bcrypt` - Password hashing

**Flow:**
1. User logs in → Backend validates credentials
2. Backend issues access + refresh tokens
3. Client stores tokens securely
4. Client sends access token in Authorization header
5. On expiry, use refresh token to get new access token

---

## 📦 State Management

### **Web: Zustand**
- Lightweight (1KB)
- Simple API
- No boilerplate
- Good TypeScript support

**Alternative:** Redux Toolkit (if you need more complex state)

### **Mobile: React Context + Hooks**
- Built into React
- Simple for MVP
- Can upgrade to Zustand later if needed

---

## 🎨 Styling

### **Web: Tailwind CSS**
- Utility-first CSS
- Fast development
- Small bundle size with purging
- Great documentation

### **Mobile: React Native StyleSheet**
- Built-in, performant
- Platform-specific styles
- Can add styled-components later if needed

---

## 📡 API Communication

### **Axios**
- Promise-based HTTP client
- Request/response interceptors
- Automatic JSON transformation
- Works in both web and mobile (with React Native)

**Setup:**
```typescript
// Base API client with interceptors
const api = axios.create({
  baseURL: process.env.API_URL,
  timeout: 10000,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## 🔄 Real-time Features

### **Socket.io**
- WebSocket library
- Fallback to polling if WebSocket unavailable
- Room/namespace support
- Great for live tracking (if sharing drives in real-time)

**Use Cases:**
- Live drive sharing (post-MVP)
- Real-time notifications
- Collaborative features

---

## ☁️ Infrastructure & Hosting

### **Backend**
**Options:**
1. **Railway** (Recommended for MVP)
   - Easy PostgreSQL setup
   - Automatic deployments
   - Free tier available
   - $5-20/month for production

2. **Heroku**
   - Easy to use
   - Add-ons for PostgreSQL
   - $7-25/month

3. **AWS (EC2 + RDS)**
   - More control
   - More complex setup
   - Pay-as-you-go

### **Frontend (Web)**
**Vercel** (Recommended)
- Made by Next.js creators
- Automatic deployments
- Free tier
- Global CDN included

**Alternative:** Netlify

### **Mobile**
**Expo EAS Build**
- Cloud builds for iOS and Android
- Free tier available
- No need for local build setup

### **Database**
**Options:**
1. **Railway PostgreSQL** - Easy, included with Railway
2. **Supabase** - PostgreSQL with real-time features, free tier
3. **AWS RDS** - Managed PostgreSQL
4. **Neon** - Serverless PostgreSQL, free tier

### **File Storage**
**AWS S3** (or compatible)
- Route data backups
- User photos
- Export files

**Alternative:** Cloudinary (for images), Backblaze B2 (cheaper)

---

## 🛠️ Development Tools

### **Version Control**
- **Git** + **GitHub** (or GitLab)

### **Package Management**
- **npm** or **yarn** or **pnpm**

### **Code Quality**
- **ESLint** - Linting
- **Prettier** - Code formatting
- **TypeScript** - Type safety
- **Husky** - Git hooks

### **Testing**
- **Jest** - Unit testing
- **React Testing Library** - Component testing
- **Supertest** - API testing

### **Monitoring**
- **Sentry** - Error tracking
- **LogRocket** - Session replay (optional)

---

## 📊 Complete Stack Summary

```
┌─────────────────────────────────────────┐
│         Mobile Apps (iOS/Android)      │
│         React Native + Expo            │
│         react-native-maps              │
└─────────────────┬───────────────────────┘
                  │
                  │ HTTPS/REST API
                  │ WebSocket (Socket.io)
                  │
┌─────────────────▼───────────────────────┐
│              Backend API                │
│         NestJS + Node.js                │
│         TypeORM                         │
└─────────────────┬───────────────────────┘
                  │
                  │ SQL Queries
                  │
┌─────────────────▼───────────────────────┐
│            PostgreSQL + PostGIS        │
│         (Geospatial Database)          │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│            Web App (Browser)            │
│         Next.js + React                 │
│         Leaflet + OpenStreetMap        │
└─────────────────────────────────────────┘
```

---

## 🚀 Why This Stack?

1. **Code Reusability**: React/TypeScript shared between web and mobile
2. **Type Safety**: TypeScript throughout reduces bugs
3. **Developer Experience**: Modern tools, great documentation
4. **Cost Effective**: Open-source first, free tiers available
5. **Scalable**: Can handle growth from MVP to production
6. **Geospatial Ready**: PostGIS is industry standard for location apps
7. **Fast Development**: Expo and Next.js speed up development

---

## 📈 Migration Path

**MVP → Production:**
- Start with Expo managed workflow → Can eject to bare React Native if needed
- Start with Railway → Can migrate to AWS later
- Start with OpenStreetMap → Can add Mapbox as premium feature
- Start simple → Add complexity as needed

---

## ✅ Final Recommendation

**For MVP:**
- React Native (Expo) + Next.js + NestJS + PostgreSQL (PostGIS) + OpenStreetMap

**This gives you:**
- Fast development
- Low cost (mostly free)
- Good performance
- Easy to scale
- Modern, maintainable codebase

Ready to start building with this stack? 🚀

