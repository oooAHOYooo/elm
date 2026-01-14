"""Budget tracking service for New Haven city spending"""
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from zoneinfo import ZoneInfo

from utils.cache import TTLCache

# Cache for budget data (longer TTL since budgets don't change daily)
_CACHE = TTLCache(ttl_seconds=86400, filepath=".cache_budget.pkl")


class BudgetTracker:
    """Tracks city budget and spending data from public sources"""
    
    def __init__(self):
        self.city_name = "New Haven"
        self.state = "CT"
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """Get cached data"""
        return _CACHE.get(key)
    
    def _set_cache(self, key: str, data: Any) -> None:
        """Cache data"""
        _CACHE.set(key, data)
    
    def _fetch_json(self, url: str, params: Optional[Dict] = None, timeout: int = 10) -> Optional[Any]:
        """Fetch JSON data from URL"""
        try:
            headers = {"User-Agent": "ElmCityDaily/1.0 (+local)"}
            resp = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None
    
    def fetch_budget_summary(self) -> Dict[str, Any]:
        """
        Fetch budget summary data from CT Open Data or city sources.
        Returns: fiscal_year, total_budget, departments (list with name, budget, spent, percentage)
        """
        cache_key = "budget:summary"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        
        # Try CT Open Data first
        ct_data_url = os.getenv("CT_BUDGET_DATA_URL", "")
        if ct_data_url:
            data = self._fetch_json(ct_data_url, params={"municipality": self.city_name})
            if data:
                result = self._parse_ct_budget_data(data)
                if result:
                    self._set_cache(cache_key, result)
                    return result
        
        # Fallback: Try to fetch from city's monthly reports endpoint
        # New Haven posts monthly financial reports at:
        # https://www.newhavenct.gov/government/departments-divisions/office-of-policy-management-and-grants/monthly-reports
        # We'll use a structured approach that can be extended
        
        # For now, return a structure that can be populated
        # In production, you'd parse actual data sources
        result = self._get_fallback_budget_data()
        self._set_cache(cache_key, result)
        return result
    
    def _parse_ct_budget_data(self, data: List[Dict]) -> Optional[Dict[str, Any]]:
        """Parse budget data from CT Open Data format"""
        if not data:
            return None
        
        # Find most recent fiscal year
        latest = max(data, key=lambda x: int(x.get("fiscal_year", 0)) if str(x.get("fiscal_year", "0")).isdigit() else 0)
        
        departments = []
        total_budget = 0
        
        # Parse department data if available
        for item in data:
            dept_name = item.get("department") or item.get("department_name") or ""
            budget = float(item.get("budgeted", 0) or item.get("budget", 0) or 0)
            spent = float(item.get("spent", 0) or item.get("expended", 0) or 0)
            
            if dept_name and budget > 0:
                departments.append({
                    "name": dept_name,
                    "budget": budget,
                    "spent": spent,
                    "remaining": budget - spent,
                    "percentage_spent": (spent / budget * 100) if budget > 0 else 0
                })
                total_budget += budget
        
        # Sort by budget size
        departments.sort(key=lambda x: x["budget"], reverse=True)
        
        return {
            "fiscal_year": latest.get("fiscal_year"),
            "total_budget": total_budget,
            "departments": departments[:15],  # Top 15 departments
            "source": "CT Open Data",
            "last_updated": datetime.now(ZoneInfo("America/New_York")).isoformat()
        }
    
    def _get_fallback_budget_data(self) -> Dict[str, Any]:
        """
        Fallback budget data structure.
        In production, this would parse actual city budget documents.
        For now, returns a structure that can be populated with real data.
        """
        # This is a template - replace with actual data parsing
        # You could scrape city budget PDFs or monthly reports here
        return {
            "fiscal_year": None,
            "total_budget": None,
            "departments": [],
            "source": "City of New Haven",
            "last_updated": datetime.now(ZoneInfo("America/New_York")).isoformat(),
            "note": "Budget data parsing not yet configured. See newhavenct.gov for official budget documents."
        }
    
    def get_spending_by_category(self) -> Dict[str, Any]:
        """Get spending breakdown by category (Public Safety, Education, etc.)"""
        summary = self.fetch_budget_summary()
        if not summary or not summary.get("departments"):
            return {"categories": []}
        
        # Group departments into categories
        categories = {
            "Public Safety": ["Police", "Fire", "Emergency"],
            "Public Works": ["Public Works", "Engineering", "Traffic"],
            "Health & Human Services": ["Health", "Social Services", "Housing"],
            "Parks & Recreation": ["Parks", "Recreation"],
            "Administration": ["Mayor", "Finance", "Legal", "HR"],
            "Education": ["Education", "Schools"],
            "Other": []
        }
        
        categorized = {cat: {"budget": 0, "spent": 0, "departments": []} for cat in categories}
        
        for dept in summary.get("departments", []):
            dept_name = dept.get("name", "").lower()
            assigned = False
            
            for category, keywords in categories.items():
                if category == "Other":
                    continue
                if any(kw.lower() in dept_name for kw in keywords):
                    categorized[category]["budget"] += dept.get("budget", 0)
                    categorized[category]["spent"] += dept.get("spent", 0)
                    categorized[category]["departments"].append(dept.get("name"))
                    assigned = True
                    break
            
            if not assigned:
                categorized["Other"]["budget"] += dept.get("budget", 0)
                categorized["Other"]["spent"] += dept.get("spent", 0)
                categorized["Other"]["departments"].append(dept.get("name"))
        
        # Calculate percentages and format
        result = []
        total_budget = summary.get("total_budget", 0) or 1  # Avoid division by zero
        
        for category, data in categorized.items():
            if data["budget"] > 0:
                result.append({
                    "category": category,
                    "budget": data["budget"],
                    "spent": data["spent"],
                    "percentage_of_total": (data["budget"] / total_budget * 100),
                    "percentage_spent": (data["spent"] / data["budget"] * 100) if data["budget"] > 0 else 0,
                    "department_count": len(data["departments"])
                })
        
        result.sort(key=lambda x: x["budget"], reverse=True)
        
        return {
            "categories": result,
            "total_budget": total_budget,
            "fiscal_year": summary.get("fiscal_year")
        }
    
    def get_budget_stats(self) -> Dict[str, Any]:
        """Get summary statistics for front page widget"""
        summary = self.fetch_budget_summary()
        
        if not summary or not summary.get("departments"):
            return {
                "fiscal_year": None,
                "total_budget": None,
                "total_spent": None,
                "percentage_spent": None,
                "department_count": 0,
                "top_department": None
            }
        
        departments = summary.get("departments", [])
        total_budget = summary.get("total_budget", 0)
        total_spent = sum(d.get("spent", 0) for d in departments)
        
        return {
            "fiscal_year": summary.get("fiscal_year"),
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": total_budget - total_spent,
            "percentage_spent": (total_spent / total_budget * 100) if total_budget > 0 else 0,
            "department_count": len(departments),
            "top_department": departments[0].get("name") if departments else None,
            "last_updated": summary.get("last_updated")
        }
