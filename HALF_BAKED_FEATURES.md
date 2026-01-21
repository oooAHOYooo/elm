# 🔧 Half-Baked Features Report

## 🚨 **Critical - Needs Immediate Attention**

### 1. **Change New Haven Live Scraper** ⚠️ **MEDIUM PRIORITY**
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

### 2. **Business Hours System** ✅ **MOSTLY COMPLETE**
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

## 🔍 **Low Priority - Nice to Have**

### 3. **Stub Events Fallback** ✅ **WORKING AS INTENDED**
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
1. **Change New Haven Live** - Register blueprint or remove module

### **Should Fix (Improves UX):**
2. **Business Hours** - Add more businesses or submission form

### **Optional:**
3. **Stub Events** - Keep as fallback

---

## 🎯 **Recommended Action Plan**

### **Phase 1: Quick Fixes (1-2 hours)**
1. **Change New Haven Live**: Either integrate or remove
   - **Option A**: Register blueprint, add to homepage
   - **Option B**: Remove module if not needed

### **Phase 2: Enhancement (4-8 hours)**
2. **Business Hours**: Add submission form
   - Public form for businesses to submit
   - Admin approval workflow
   - Email notifications

---

## 📝 **Files That Need Attention**

### **Critical:**
- `app.py` - Register Change New Haven blueprint (or remove module)

### **Medium:**
- `templates/business_hours/manage.html` - Add public submission form

### **Low:**
- `services/events.py` - Keep stub events (working as intended)

---

**Bottom Line**: The site is **95% production-ready**. The Change New Haven scraper is the main incomplete feature (exists but not registered). Business hours works but needs more data. Budget tracker and SeeClickFix have been removed.
