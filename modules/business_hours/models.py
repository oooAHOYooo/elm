"""Data models for business hours"""
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class BusinessHours:
    """Represents hours for a single day"""
    day: str  # Monday, Tuesday, etc.
    open_time: Optional[str] = None  # Format: "HH:MM" (24-hour)
    close_time: Optional[str] = None  # Format: "HH:MM" (24-hour)
    is_closed: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BusinessHours':
        return cls(**data)
    
    def format_time(self, time_str: Optional[str]) -> str:
        """Convert 24-hour time to 12-hour format"""
        if not time_str:
            return ""
        try:
            hour, minute = map(int, time_str.split(":"))
            period = "AM" if hour < 12 else "PM"
            hour_12 = hour if hour <= 12 else hour - 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12}:{minute:02d} {period}"
        except:
            return time_str
    
    def display(self) -> str:
        """Get display string for these hours"""
        if self.is_closed:
            return "Closed"
        if not self.open_time or not self.close_time:
            return "Hours vary"
        return f"{self.format_time(self.open_time)} - {self.format_time(self.close_time)}"


@dataclass
class Business:
    """Represents a business with its hours"""
    id: str
    name: str
    category: str  # restaurant, retail, service, etc.
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[List[BusinessHours]] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def __post_init__(self):
        if self.hours is None:
            self.hours = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'hours': [h.to_dict() for h in self.hours] if self.hours else []
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Business':
        hours_data = data.get('hours', [])
        hours = [BusinessHours.from_dict(h) for h in hours_data] if hours_data else []
        return cls(
            id=data['id'],
            name=data['name'],
            category=data.get('category', 'other'),
            address=data.get('address'),
            phone=data.get('phone'),
            website=data.get('website'),
            hours=hours,
            notes=data.get('notes'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )





