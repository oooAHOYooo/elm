"""Legislation tracking service"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from zoneinfo import ZoneInfo
from collections import defaultdict

from services.civics import fetch_recent_matters
from utils.cache import TTLCache

# Cache for processed legislation data
_legislation_cache = TTLCache(ttl_seconds=600, filepath=".cache_legislation.pkl")


class LegislationTracker:
    """Tracks passed legislation from New Haven's Legistar system"""
    
    def __init__(self, city_slug: str = "newhaven"):
        self.city_slug = city_slug
        self.passed_statuses = {"Adopted", "Passed", "Approved", "Enacted"}
    
    def get_passed_legislation(
        self, 
        days_back: int = 90,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """Get all passed legislation within the specified timeframe"""
        # Check cache for filtered results
        cache_key = f"passed_legislation:{self.city_slug}:{days_back}:{limit}"
        cached = _legislation_cache.get(cache_key)
        if cached is not None:
            return cached
        
        matters = fetch_recent_matters(
            city_slug=self.city_slug,
            days_back=days_back,
            limit=limit,
            ttl_seconds=600
        )
        
        # Filter for passed legislation
        passed = [
            m for m in matters 
            if (m.get("status") or "") in self.passed_statuses
        ]
        
        # Sort by date (newest first)
        passed.sort(key=lambda x: x.get("date_iso") or "", reverse=True)
        
        # Cache the filtered results
        _legislation_cache.set(cache_key, passed)
        return passed
    
    def group_by_week(self, legislation: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group legislation by week (Monday-Sunday)"""
        grouped = defaultdict(list)
        tz = ZoneInfo("America/New_York")
        
        for item in legislation:
            date_iso = item.get("date_iso")
            if not date_iso:
                continue
            
            try:
                dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
                dt_local = dt.astimezone(tz)
                
                # Get Monday of the week
                days_to_monday = (dt_local.weekday()) % 7
                week_start = dt_local - timedelta(days=days_to_monday)
                week_key = week_start.strftime("%Y-%m-%d")
                week_label = week_start.strftime("%b %d, %Y")
                
                grouped[week_key].append({
                    **item,
                    "week_label": week_label
                })
            except Exception:
                continue
        
        # Sort weeks (newest first)
        sorted_weeks = sorted(grouped.items(), key=lambda x: x[0], reverse=True)
        
        return {
            week_key: sorted(items, key=lambda x: x.get("date_iso") or "", reverse=True)
            for week_key, items in sorted_weeks
        }
    
    def group_by_month(self, legislation: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group legislation by month"""
        grouped = defaultdict(list)
        tz = ZoneInfo("America/New_York")
        
        for item in legislation:
            date_iso = item.get("date_iso")
            if not date_iso:
                continue
            
            try:
                dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
                dt_local = dt.astimezone(tz)
                
                month_key = dt_local.strftime("%Y-%m")
                month_label = dt_local.strftime("%B %Y")
                
                grouped[month_key].append({
                    **item,
                    "month_label": month_label
                })
            except Exception:
                continue
        
        # Sort months (newest first)
        sorted_months = sorted(grouped.items(), key=lambda x: x[0], reverse=True)
        
        return {
            month_key: sorted(items, key=lambda x: x.get("date_iso") or "", reverse=True)
            for month_key, items in sorted_months
        }
    
    def get_monthly_counts(self, legislation: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get count of passed legislation per month"""
        monthly = self.group_by_month(legislation)
        
        counts = []
        for month_key, items in sorted(monthly.items(), key=lambda x: x[0], reverse=True):
            if items:
                month_label = items[0].get("month_label", month_key)
                counts.append({
                    "month": month_key,
                    "month_label": month_label,
                    "count": len(items)
                })
        
        return counts
    
    def get_stats(self, legislation: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get overall statistics"""
        tz = ZoneInfo("America/New_York")
        now = datetime.now(tz)
        
        # This week (Monday-Sunday)
        days_to_monday = (now.weekday()) % 7
        week_start = now - timedelta(days=days_to_monday)
        week_end = week_start + timedelta(days=7)
        
        # This month
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        this_week_count = 0
        this_month_count = 0
        
        for item in legislation:
            date_iso = item.get("date_iso")
            if not date_iso:
                continue
            
            try:
                dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
                dt_local = dt.astimezone(tz)
                
                if week_start <= dt_local < week_end:
                    this_week_count += 1
                
                if month_start <= dt_local < month_end:
                    this_month_count += 1
            except Exception:
                continue
        
        return {
            "total_passed": len(legislation),
            "this_week": this_week_count,
            "this_month": this_month_count,
            "last_30_days": len([
                item for item in legislation
                if item.get("date_iso") and 
                (datetime.fromisoformat(item["date_iso"].replace("Z", "+00:00")).astimezone(tz) >= now - timedelta(days=30))
            ])
        }
