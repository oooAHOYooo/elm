"""Storage layer for business hours data"""
import json
import os
from typing import List, Optional, Dict
from pathlib import Path
from .models import Business, BusinessHours

# Default days of the week
DAYS_OF_WEEK = [
    "Monday", "Tuesday", "Wednesday", "Thursday", 
    "Friday", "Saturday", "Sunday"
]


class BusinessHoursStorage:
    """Manages storage and retrieval of business hours data"""
    
    def __init__(self, data_file: str = "data/business_hours.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create data file if it doesn't exist"""
        if not self.data_file.exists():
            self._write_data([])
    
    def _read_data(self) -> List[Dict]:
        """Read all businesses from storage"""
        try:
            if not self.data_file.exists():
                return []
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    
    def _write_data(self, businesses: List[Dict]):
        """Write businesses to storage"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(businesses, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise Exception(f"Failed to write business hours data: {e}")
    
    def get_all_businesses(self) -> List[Business]:
        """Get all businesses"""
        data = self._read_data()
        return [Business.from_dict(b) for b in data]
    
    def get_business(self, business_id: str) -> Optional[Business]:
        """Get a specific business by ID"""
        businesses = self.get_all_businesses()
        for business in businesses:
            if business.id == business_id:
                return business
        return None
    
    def create_business(self, business: Business) -> Business:
        """Create a new business"""
        businesses = self.get_all_businesses()
        # Check if ID already exists
        if any(b.id == business.id for b in businesses):
            raise ValueError(f"Business with ID '{business.id}' already exists")
        businesses.append(business)
        self._write_data([b.to_dict() for b in businesses])
        return business
    
    def update_business(self, business_id: str, updates: Dict) -> Optional[Business]:
        """Update an existing business"""
        businesses = self.get_all_businesses()
        for i, business in enumerate(businesses):
            if business.id == business_id:
                # Update fields
                for key, value in updates.items():
                    if key == 'hours' and isinstance(value, list):
                        business.hours = [BusinessHours.from_dict(h) for h in value]
                    elif hasattr(business, key):
                        setattr(business, key, value)
                from datetime import datetime
                business.updated_at = datetime.now().isoformat()
                businesses[i] = business
                self._write_data([b.to_dict() for b in businesses])
                return business
        return None
    
    def delete_business(self, business_id: str) -> bool:
        """Delete a business"""
        businesses = self.get_all_businesses()
        original_count = len(businesses)
        businesses = [b for b in businesses if b.id != business_id]
        if len(businesses) < original_count:
            self._write_data([b.to_dict() for b in businesses])
            return True
        return False
    
    def search_businesses(self, query: str = None, category: str = None) -> List[Business]:
        """Search businesses by name or filter by category"""
        businesses = self.get_all_businesses()
        
        if query:
            query_lower = query.lower()
            businesses = [
                b for b in businesses 
                if query_lower in b.name.lower() or 
                   (b.address and query_lower in b.address.lower())
            ]
        
        if category:
            businesses = [b for b in businesses if b.category.lower() == category.lower()]
        
        return businesses





