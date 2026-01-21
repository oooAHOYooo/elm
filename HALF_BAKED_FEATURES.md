# 🔧 Half-Baked Features Report

## 🚨 **Critical - Needs Immediate Attention**

### 1. **Budget Tracker** ⚠️ **HIGH PRIORITY**
**Status**: Fully implemented system, but **NO DATA SOURCE**

**What's Done:**
- ✅ Complete module (`modules/budget_tracker/tracker.py`)
- ✅ Frontend page (`templates/budget/tracker.html`)
- ✅ API endpoint (`/api/budget`)
- ✅ Homepage widget
- ✅ Caching system
- ✅ Category grouping logic

**What's Missing:**
- ❌ No data source configured (`CT_BUDGET_DATA_URL` env var not set)
- ❌ Returns empty/placeholder data
- ❌ Shows "loading..." message on homepage

**Impact:**
- Homepage widget is non-functional
- Full budget page shows "no data available" message
- Feature appears broken to users

**How to Fix:**
1. **Option A**: Configure `CT_BUDGET_DATA_URL` environment variable
   - Find CT Open Data budget dataset URL
   - Set in `.env`: `CT_BUDGET_DATA_URL=https://data.ct.gov/api/views/xxxx`
   
2. **Option B**: Implement PDF scraper for city budget documents
   - Scrape from: https://www.newhavenct.gov/government/departments-divisions/office-of-policy-management-and-grants/monthly-reports
   - Parse monthly financial reports
   - Extract department spending data

3. **Option C**: Hide widget until data source is ready
   - Remove from homepage
   - Keep page accessible but show "coming soon"

**Files:**
- `modules/budget_tracker/tracker.py` (lines 50, 108-123)
- `templates/budget/tracker.html` (line 135)
- `app.py` (lines 211-216, 681-722)

---

### 2. **Change New Haven Live Scraper** ⚠️ **MEDIUM PRIORITY**
**Status**: Module exists but **NOT REGISTERED/INTEGRATED**

**What's Done:**
- ✅ Complete scraper module (`modules/change_new_haven_live/scraper.py`)
- ✅ Blueprint with API route (`modules/change_new_haven_live/routes.py`)
- ✅ Caching system (30-minute TTL)
- ✅ Keyword-based link extraction from city website

**What's Missing:**
- ❌ Blueprint not registered in `app.py`
- ❌ Route `/api/change-new-haven-live` doesn't work
- ❌ No frontend integration
- ❌ Not linked anywhere in the UI

**Impact:**
- Feature is completely inaccessible
- Code exists but is dead/unused
- Potential useful civic links scraper is wasted

**How to Fix:**
1. Register blueprint in `app.py`:
   ```python
   from modules.change_new_haven_live.routes import bp as change_new_haven_bp
   app.register_blueprint(change_new_haven_bp)
   ```

2. Add to homepage or create dedicated page
3. Integrate into Quick Links or create new section
4. Test scraper (may need to update keywords)

**Files:**
- `modules/change_new_haven_live/routes.py` (complete but unused)
- `modules/change_new_haven_live/scraper.py` (complete but unused)
- `app.py` (missing registration)

---

## ⚠️ **Medium Priority - Partially Working**

### 3. **Business Hours System** ✅ **MOSTLY COMPLETE**
**Status**: System works, but needs real data population

**What's Done:**
- ✅ Full CRUD system (create, read, update, delete)
- ✅ Management interface (`/business-hours/manage`)
- ✅ Public listing page (`/business-hours`)
- ✅ API endpoints
- ✅ Data storage (JSON-based)
- ✅ Search and filtering
- ✅ Real businesses in `data/hours.json` (Rudy's Bar, Owl Shop, etc.)

**What's Missing:**
- ⚠️ Only ~10 businesses in database
- ⚠️ No bulk import functionality
- ⚠️ No business verification/approval system
- ⚠️ No user-submission form (only admin interface)

**Impact:**
- Feature works but has limited data
- Users can't submit their own businesses
- Directory is small

**How to Fix:**
1. **Option A**: Add public submission form
   - Allow businesses to submit their own hours
   - Add approval workflow (admin approves submissions)
   
2. **Option B**: Bulk import from existing directories
   - Import from Google Maps, Yelp, etc.
   - Validate and clean data
   
3. **Option C**: Manual population
   - Add more businesses manually via admin interface
   - Focus on popular/downtown businesses first

**Files:**
- `modules/business_hours/` (all complete)
- `data/hours.json` (has real data, just limited)
- `templates/business_hours/` (complete)

---

### 4. **SeeClickFix Integration** ⚠️ **MENTIONED BUT NOT IMPLEMENTED**
**Status**: Referenced in Quick Links, but no data tracking

**What's Done:**
- ✅ Link in Quick Links popup
- ✅ Reference in documentation

**What's Missing:**
- ❌ No API integration
- ❌ No statistics dashboard
- ❌ No issue tracking
- ❌ No data display

**Impact:**
- Users can click through to SeeClickFix, but no data on site
- Missed opportunity for civic engagement feature

**How to Fix:**
1. Implement SeeClickFix API integration:
   ```python
   # SeeClickFix API: https://seeclickfix.com/api/v2/issues
   # No auth required for public data
   ```

2. Create statistics dashboard:
   - Open/closed issues by category
   - Response times
   - Most-reported issues
   - Neighborhood breakdown

3. Add to homepage or create dedicated page

**Files:**
- `templates/index.html` (has link, no data)
- Need to create: `modules/seeclickfix/` module

---

## 🔍 **Low Priority - Nice to Have**

### 5. **Stub Events Fallback** ✅ **WORKING AS INTENDED**
**Status**: Fallback system, only used when feeds fail

**What's Done:**
- ✅ Fallback events in `services/events.py`
- ✅ Only shows when RSS feeds are empty

**Recommendation:**
- ✅ **Keep as-is** - This is a good fallback
- Only shows if real feeds fail (rare)
- Provides better UX than empty calendar

---

## 📊 **Summary**

### **Must Fix (Blocks Production):**
1. **Budget Tracker** - Configure data source or hide widget
2. **Change New Haven Live** - Register blueprint or remove module

### **Should Fix (Improves UX):**
3. **Business Hours** - Add more businesses or submission form
4. **SeeClickFix** - Implement API integration

### **Optional:**
5. **Stub Events** - Keep as fallback

---

## 🎯 **Recommended Action Plan**

### **Phase 1: Quick Fixes (1-2 hours)**
1. **Budget Tracker**: Hide widget on homepage until data source configured
   - Comment out budget widget in `templates/index.html`
   - Keep page accessible but show "coming soon"
   
2. **Change New Haven Live**: Either integrate or remove
   - **Option A**: Register blueprint, add to homepage
   - **Option B**: Remove module if not needed

### **Phase 2: Data Integration (2-4 hours)**
3. **Budget Tracker**: Configure data source
   - Research CT Open Data budget datasets
   - Set `CT_BUDGET_DATA_URL` environment variable
   - Test data parsing

4. **SeeClickFix**: Implement basic integration
   - Create module for API calls
   - Add statistics to homepage
   - Show top issues by category

### **Phase 3: Enhancement (4-8 hours)**
5. **Business Hours**: Add submission form
   - Public form for businesses to submit
   - Admin approval workflow
   - Email notifications

---

## 📝 **Files That Need Attention**

### **Critical:**
- `app.py` - Register Change New Haven blueprint (or remove module)
- `templates/index.html` - Hide budget widget or configure data source
- `.env` - Add `CT_BUDGET_DATA_URL` if implementing budget data

### **Medium:**
- `modules/budget_tracker/tracker.py` - Implement PDF scraper if no API
- `templates/business_hours/manage.html` - Add public submission form
- Create `modules/seeclickfix/` - New module for SeeClickFix integration

### **Low:**
- `services/events.py` - Keep stub events (working as intended)

---

**Bottom Line**: The site is **90% production-ready**. The budget tracker and Change New Haven scraper are the main incomplete features. Business hours works but needs more data. SeeClickFix is mentioned but not implemented.
