# 🔧 Incomplete Features & Improvement Opportunities

## 🚨 **Critical - Unused/Dead Code**

### 1. **Change New Haven Live Scraper** ⚠️ **HIGH PRIORITY**
**Status**: Complete module but **NOT REGISTERED/INTEGRATED**

**What Exists:**
- ✅ Complete scraper (`modules/change_new_haven_live/scraper.py`)
- ✅ Blueprint with API route (`modules/change_new_haven_live/routes.py`)
- ✅ JavaScript file (`static/js/change_new_haven_live.js`)
- ✅ Caching system (30-minute TTL)
- ✅ Keyword-based link extraction

**What's Missing:**
- ❌ Blueprint not registered in `app.py`
- ❌ Route `/api/change-new-haven-live` doesn't work
- ❌ No frontend integration
- ❌ Not linked anywhere in UI
- ❌ JavaScript file unused

**Impact:**
- Dead code taking up space
- Useful civic links scraper wasted
- Confusing for future developers

**How to Fix:**
1. **Option A**: Integrate it
   ```python
   # In app.py, add:
   from modules.change_new_haven_live.routes import bp as change_new_haven_bp
   app.register_blueprint(change_new_haven_bp)
   ```
   - Add to Quick Links or create dedicated page
   - Test scraper functionality

2. **Option B**: Remove it
   - Delete `modules/change_new_haven_live/`
   - Delete `static/js/change_new_haven_live.js`
   - Clean up any references

**Files:**
- `modules/change_new_haven_live/` (entire module unused)
- `static/js/change_new_haven_live.js` (unused)
- `app.py` (missing registration)

---

## ⚠️ **Medium Priority - Partially Working**

### 2. **Business Hours - Limited Data** ⚠️
**Status**: System works, but needs more businesses

**What's Done:**
- ✅ Full CRUD system
- ✅ Management interface
- ✅ Public listing
- ✅ ~10 real businesses in database

**What's Missing:**
- ⚠️ Only ~10 businesses (directory is small)
- ⚠️ No public submission form
- ⚠️ No bulk import
- ⚠️ No business verification system

**Impact:**
- Feature works but limited utility
- Users can't contribute
- Directory feels incomplete

**How to Fix:**
1. Add public submission form with approval workflow
2. Bulk import from Google Maps/Yelp
3. Manual population of popular businesses

**Files:**
- `modules/business_hours/` (complete, just needs data)
- `data/hours.json` (has real data, just limited)

---

### 3. **Parking Data - Placeholder Values** ⚠️
**Status**: Shows fake/placeholder data

**What's Wrong:**
- Parking popup shows hardcoded values:
  - "Temple St: 🟢 Available (342/500)"
  - "Crown St: 🟡 Filling (89/200)"
  - These are static, not real-time

**Impact:**
- Misleading to users
- Appears functional but isn't

**How to Fix:**
1. **Option A**: Integrate real parking API
   - Find New Haven parking authority API
   - Fetch real-time availability
   - Update every 1-2 minutes

2. **Option B**: Remove fake data
   - Show "Data not available" message
   - Link to parking authority website
   - Remove misleading numbers

**Files:**
- `templates/index.html` (lines ~725-730, parking popup)

---

### 4. **Function Naming - Misleading** ⚠️
**Status**: Function name suggests sample data but uses real data

**What's Wrong:**
- Function `_sample_hours_neighborhoods()` in `app.py`
- Name suggests "sample" but actually loads real data from `data/hours.json`
- Confusing for developers

**Impact:**
- Code clarity issue
- Misleading function name

**How to Fix:**
- Rename to `_load_hours_neighborhoods()` or `_get_hours_neighborhoods()`

**Files:**
- `app.py` (line 39, function name)

---

## 🔍 **Low Priority - Nice to Have**

### 5. **SEO & Meta Tags - Basic** 📊
**Status**: Minimal SEO implementation

**What's Done:**
- ✅ Basic meta description
- ✅ Viewport meta tag
- ✅ Title tag

**What's Missing:**
- ❌ No Open Graph tags (og:title, og:description, og:image)
- ❌ No Twitter Card tags
- ❌ No structured data (JSON-LD)
- ❌ No canonical URL
- ❌ No robots meta tag

**Impact:**
- Poor social media sharing previews
- Lower search engine visibility
- Missing rich snippets

**How to Fix:**
- Add Open Graph tags for better social sharing
- Add Twitter Card tags
- Add JSON-LD structured data for events, organization
- Add canonical URLs

**Files:**
- `templates/base.html` (head section)

---

### 6. **Accessibility - No Audit** ♿
**Status**: Basic accessibility, but no formal audit

**What's Done:**
- ✅ Semantic HTML
- ✅ ARIA labels in some places
- ✅ Keyboard navigation (D for dark mode, R for refresh)

**What's Missing:**
- ⚠️ No formal WCAG 2.1 audit
- ⚠️ Some popups may need better keyboard navigation
- ⚠️ Color contrast not verified
- ⚠️ Screen reader testing not done

**Impact:**
- May not meet accessibility standards
- Could exclude some users

**How to Fix:**
- Run accessibility audit (axe DevTools, WAVE)
- Test with screen readers
- Verify color contrast ratios
- Improve keyboard navigation

---

### 7. **Error Handling - Console Logs** 🐛
**Status**: Some errors only logged to console

**What's Wrong:**
- `console.error()` calls in JavaScript
- Errors not visible to users
- No error reporting/analytics

**Impact:**
- Silent failures
- Hard to debug user issues
- No error tracking

**How to Fix:**
- Add user-visible error messages
- Consider error reporting service (Sentry, etc.)
- Better error handling in API calls

**Files:**
- `static/js/dashboard.js` (lines 588, 813)

---

### 8. **Sponsor Placeholder - Visible** 💰
**Status**: Placeholder sponsor still visible

**What's Wrong:**
- "Your Business Here" placeholder visible on homepage
- Looks unprofessional

**Impact:**
- Appears incomplete
- Unprofessional appearance

**How to Fix:**
- Remove placeholder if no sponsors
- Or hide section if empty
- Or add real sponsors

**Files:**
- `templates/index.html` (line ~399, sponsor placeholder)

---

### 9. **Documentation - Outdated References** 📝
**Status**: Docs reference removed features

**What's Wrong:**
- `HALF_BAKED_FEATURES.md` still mentions budget tracker (removed)
- `HALF_BAKED_FEATURES.md` still mentions SeeClickFix (removed)
- Other docs may have outdated info

**Impact:**
- Confusing documentation
- Misleading for developers

**How to Fix:**
- Update `HALF_BAKED_FEATURES.md` to remove budget/SeeClickFix sections
- Review other docs for outdated references
- Keep docs in sync with code

**Files:**
- `HALF_BAKED_FEATURES.md` (needs update)
- `README.md` (may need review)
- `MVP_FEATURES.md` (may need review)

---

### 10. **JavaScript Organization** 📦
**Status**: Multiple JS files, some unused

**What Exists:**
- `dashboard.js` - Main dashboard JS ✅ Used
- `clock.js` - Clock functionality ✅ Used
- `mobile-nav.js` - Mobile navigation ✅ Used
- `business_hours.js` - Business hours management ✅ Used
- `change_new_haven_live.js` - ❌ **UNUSED** (module not integrated)

**Impact:**
- Unused file taking up space
- Confusing file structure

**How to Fix:**
- Remove `change_new_haven_live.js` if module not integrated
- Or integrate module and use the JS file

**Files:**
- `static/js/change_new_haven_live.js` (unused)

---

## 📊 **Summary by Priority**

### **Must Fix (Dead Code):**
1. **Change New Haven Live** - Integrate or remove
2. **change_new_haven_live.js** - Remove if module not integrated

### **Should Fix (User-Facing Issues):**
3. **Parking Data** - Remove fake data or integrate real API
4. **Business Hours** - Add more businesses or submission form
5. **Function Naming** - Rename `_sample_hours_neighborhoods()`
6. **Sponsor Placeholder** - Remove or hide

### **Nice to Have (Polish):**
7. **SEO/Meta Tags** - Add Open Graph, Twitter Cards, structured data
8. **Accessibility** - Run audit and fix issues
9. **Error Handling** - Better user-facing error messages
10. **Documentation** - Update outdated references

---

## 🎯 **Recommended Action Plan**

### **Phase 1: Clean Up Dead Code (30 minutes)**
1. **Change New Haven Live**: Decide to integrate or remove
   - If remove: Delete module and JS file
   - If integrate: Register blueprint, add to UI

2. **Documentation**: Update `HALF_BAKED_FEATURES.md`
   - Remove budget tracker section
   - Remove SeeClickFix section
   - Update status

### **Phase 2: Fix User-Facing Issues (1-2 hours)**
3. **Parking Data**: Remove fake numbers or add real API
4. **Function Naming**: Rename `_sample_hours_neighborhoods()`
5. **Sponsor Placeholder**: Hide if no sponsors

### **Phase 3: Enhancements (2-4 hours)**
6. **SEO**: Add Open Graph, Twitter Cards, structured data
7. **Business Hours**: Add public submission form or bulk import
8. **Error Handling**: Better user-facing error messages

### **Phase 4: Polish (4-8 hours)**
9. **Accessibility**: Run audit, fix issues
10. **Documentation**: Full review and update

---

## 📝 **Quick Wins (Under 1 Hour Each)**

1. ✅ **Rename function** - `_sample_hours_neighborhoods()` → `_load_hours_neighborhoods()`
2. ✅ **Remove placeholder** - Hide sponsor section if empty
3. ✅ **Update docs** - Remove budget/SeeClickFix from HALF_BAKED_FEATURES.md
4. ✅ **Remove fake parking data** - Show "Data not available" instead
5. ✅ **Delete unused JS** - Remove `change_new_haven_live.js` if module not integrated

---

**Bottom Line**: The site is **~95% production-ready**. Main issues are:
- Dead code (Change New Haven Live module)
- Placeholder/fake data (parking, sponsor)
- Minor polish (SEO, accessibility, naming)

Most critical: **Decide on Change New Haven Live** - integrate it or remove it.
