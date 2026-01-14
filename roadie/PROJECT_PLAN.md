# Carva - Driving Journal App
## Project Plan & MVP Features

### 🎯 Vision
A fitness app for your car - track your drives, explore your routes, and maintain a digital journal of your automotive adventures.

---

## 📋 MVP Features Recommendation

### Core Features (Must Have)
1. **Drive Recording**
   - Start/stop drive tracking
   - Real-time GPS tracking
   - Background location tracking
   - Auto-pause when stopped
   - Manual pause/resume

2. **Drive History & Visualization**
   - List of all recorded drives
   - Interactive map showing route
   - Drive details (date, time, duration, distance)
   - Route playback/animation

3. **Basic Statistics**
   - Total distance driven
   - Total time driving
   - Number of drives
   - Average drive distance
   - Monthly/weekly summaries

4. **Drive Details**
   - Full route map
   - Distance traveled
   - Duration
   - Average speed
   - Max speed
   - Start/end locations
   - Elevation profile (if available)

5. **User Account**
   - Sign up / Sign in
   - Profile management
   - Drive data sync across devices

### Nice-to-Have (Post-MVP)
- Social features (share drives, follow friends)
- Drive photos
- Vehicle management (multiple cars)
- Drive tags/categories (commute, road trip, etc.)
- Export drives (GPX, KML)
- Drive notes/journal entries
- Weather data during drives
- Fuel efficiency tracking
- Drive challenges/goals

---

## 🏗️ Technical Architecture

### Tech Stack Recommendation

#### Mobile Apps (iOS & Android)
- **Framework**: React Native with Expo
  - Cross-platform development
  - Built-in location services
  - Easy deployment
  - Access to native APIs

#### Web App
- **Framework**: React (Next.js)
  - Server-side rendering
  - SEO friendly
  - Modern UI capabilities

#### Backend
- **Runtime**: Node.js with Express or NestJS
- **Database**: PostgreSQL (for structured data) + PostGIS (for geospatial data)
- **File Storage**: AWS S3 or similar (for route data, images)
- **Authentication**: JWT tokens
- **Real-time**: WebSockets (Socket.io) for live tracking

#### Maps
- **Primary**: OpenStreetMap with Leaflet (web) / React Native Maps (mobile)
- **Alternative**: Mapbox (has free tier, better performance)
- **Fallback**: Google Maps API (if budget allows)

#### Infrastructure
- **Hosting**: 
  - Backend: AWS, Heroku, or Railway
  - Frontend: Vercel or Netlify
  - Mobile: Expo EAS Build
- **CDN**: CloudFront or Cloudflare
- **Monitoring**: Sentry for error tracking

---

## 📐 Database Schema

### Users Table
```
- id (UUID, primary key)
- email (string, unique)
- password_hash (string)
- name (string)
- created_at (timestamp)
- updated_at (timestamp)
```

### Drives Table
```
- id (UUID, primary key)
- user_id (UUID, foreign key)
- name (string, nullable) - user can name their drive
- start_time (timestamp)
- end_time (timestamp)
- distance (float, meters)
- duration (integer, seconds)
- average_speed (float, km/h)
- max_speed (float, km/h)
- start_location (POINT)
- end_location (POINT)
- route_data (JSONB or reference to route_points)
- created_at (timestamp)
- updated_at (timestamp)
```

### Route Points Table
```
- id (UUID, primary key)
- drive_id (UUID, foreign key)
- latitude (float)
- longitude (float)
- altitude (float, nullable)
- speed (float, nullable)
- timestamp (timestamp)
- sequence (integer) - order in route
```

### Indexes
- Spatial index on route_points (latitude, longitude)
- Index on drives (user_id, start_time)
- Index on route_points (drive_id, sequence)

---

## 🎨 UI/UX Design Considerations

### Mobile App
- **Home Screen**: 
  - Large "Start Drive" button
  - Recent drives list
  - Quick stats (total distance, drives this week)
  
- **Active Drive Screen**:
  - Live map with current location
  - Distance, time, speed display
  - Pause/Stop buttons
  - Minimize to background option

- **Drive History Screen**:
  - Grid/list view of drives
  - Filter by date range
  - Search functionality

- **Drive Detail Screen**:
  - Full route map
  - Statistics cards
  - Timeline/playback option
  - Edit name/notes

### Web App
- **Dashboard**: 
  - Overview map with all drives
  - Statistics widgets
  - Recent drives list
  
- **Drive Detail**: 
  - Large interactive map
  - Detailed statistics
  - Export options

---

## 🔐 Security & Privacy

1. **Data Encryption**
   - HTTPS/TLS for all API calls
   - Encrypted location data at rest
   - Secure password hashing (bcrypt)

2. **Privacy**
   - User controls data visibility
   - Option to delete drives
   - GDPR compliance considerations
   - Location data only stored when actively recording

3. **Authentication**
   - JWT tokens with refresh tokens
   - Secure session management
   - Password reset functionality

---

## 📱 Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Project setup (React Native, Next.js, Backend)
- [ ] Database schema and migrations
- [ ] User authentication (sign up, sign in)
- [ ] Basic API structure

### Phase 2: Core Tracking (Week 3-4)
- [ ] GPS location tracking service
- [ ] Start/stop drive functionality
- [ ] Route point collection
- [ ] Background location tracking
- [ ] Drive save/retrieve API

### Phase 3: Visualization (Week 5-6)
- [ ] Map integration (OpenStreetMap/Leaflet)
- [ ] Route rendering on map
- [ ] Drive list UI
- [ ] Drive detail view
- [ ] Basic statistics calculation

### Phase 4: Polish & Testing (Week 7-8)
- [ ] UI/UX improvements
- [ ] Error handling
- [ ] Performance optimization
- [ ] Testing (unit, integration)
- [ ] Bug fixes

### Phase 5: Deployment (Week 9)
- [ ] Production environment setup
- [ ] Mobile app builds (iOS & Android)
- [ ] Web app deployment
- [ ] Monitoring setup
- [ ] Documentation

---

## 🗺️ Map Solution Details

### OpenStreetMap + Leaflet (Recommended for MVP)
**Pros:**
- Completely free and open source
- No API keys required
- Good for basic route visualization
- Customizable styling

**Cons:**
- Requires tile server (can use free public servers)
- May have rate limits on public servers
- Less polished than commercial solutions

**Implementation:**
- Web: Leaflet.js with OpenStreetMap tiles
- Mobile: react-native-maps with OpenStreetMap provider

### Mapbox (Alternative)
**Pros:**
- Better performance
- Beautiful default styling
- Good documentation
- Free tier: 50,000 map loads/month

**Cons:**
- Requires API key
- Costs after free tier
- Less "open source" feel

---

## 📊 Key Metrics to Track

1. **User Engagement**
   - Number of drives recorded
   - Average drives per user
   - Active users (daily/weekly/monthly)

2. **Technical**
   - GPS accuracy
   - Battery usage
   - App crashes
   - API response times

3. **Business** (if monetizing later)
   - User retention
   - Feature usage
   - Conversion rates

---

## 🚀 Getting Started Checklist

### Development Environment
- [ ] Node.js 18+ installed
- [ ] PostgreSQL with PostGIS extension
- [ ] Expo CLI installed
- [ ] Git repository initialized
- [ ] Code editor setup (VS Code recommended)

### Accounts Needed
- [ ] Expo account (for mobile builds)
- [ ] Map provider account (if using Mapbox)
- [ ] Cloud hosting account (AWS/Heroku/Railway)
- [ ] Domain name (optional)

### Testing Devices
- [ ] iOS device or simulator
- [ ] Android device or emulator
- [ ] Web browser (Chrome, Firefox, Safari)

---

## 🔄 Data Flow

### Recording a Drive
1. User taps "Start Drive"
2. App requests location permissions
3. Location service starts tracking
4. GPS coordinates collected every 5-10 seconds
5. Data sent to backend in batches (every 30 seconds or 10 points)
6. User taps "Stop Drive"
7. Final route data sent to backend
8. Backend calculates statistics
9. Drive saved to database
10. User redirected to drive detail view

### Viewing a Drive
1. User navigates to drive history
2. App requests drive list from API
3. Backend queries database
4. Returns drive metadata (not full route)
5. User taps on a drive
6. App requests full drive details + route points
7. Backend returns route data
8. Map renders route polyline
9. Statistics displayed

---

## 💡 Future Enhancements (Post-MVP)

1. **Social Features**
   - Share drives publicly
   - Follow other users
   - Comments on drives
   - Drive recommendations

2. **Advanced Analytics**
   - Heat maps of frequently traveled routes
   - Speed analysis
   - Time-of-day patterns
   - Route comparisons

3. **Vehicle Management**
   - Multiple vehicles
   - Vehicle-specific statistics
   - Maintenance reminders
   - Fuel tracking

4. **Export & Integration**
   - GPX export
   - Google Maps integration
   - Calendar integration
   - Health app integration (for steps/activity)

5. **Gamification**
   - Achievements/badges
   - Challenges
   - Leaderboards
   - Streaks

---

## 📝 Notes

- **Location Accuracy**: Consider using both GPS and network location for better accuracy
- **Battery Optimization**: Batch location updates, reduce update frequency when stationary
- **Offline Support**: Cache recent drives, queue uploads when offline
- **Privacy First**: Make it clear to users how location data is used and stored
- **Performance**: Optimize map rendering for long routes (simplify polyline, use clustering)

---

## ✅ Ready to Build?

This plan provides a solid foundation for building Carva. The MVP focuses on core functionality while leaving room for future expansion. Once you approve this plan, we can begin implementation!

**Next Steps:**
1. Review and approve this plan
2. Set up development environment
3. Initialize project structure
4. Begin Phase 1 implementation

