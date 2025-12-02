from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo


@dataclass
class Event:
    title: str
    start: datetime
    end: Optional[datetime]
    location: str
    category: str
    description: str
    link: Optional[str] = None


def get_upcoming_events(tz: ZoneInfo, max_events: int = 6) -> List[Event]:
    """
    Return a small stubbed list of upcoming events in/around New Haven.
    """
    now = datetime.now(tz)
    base_date = now.replace(hour=18, minute=0, second=0, microsecond=0)
    events: List[Event] = [
        Event(
            title="City Hall Public Hearing: Zoning Updates",
            start=base_date + timedelta(days=1),
            end=None,
            location="165 Church St, New Haven",
            category="Civics",
            description="Discussion on proposed zoning text amendments and community feedback.",
            link=None,
        ),
        Event(
            title="Wooster Square Farmers' Market",
            start=base_date.replace(hour=10) + timedelta(days=(5 - now.weekday()) % 7),
            end=None,
            location="Russo Park, New Haven",
            category="Community",
            description="Fresh produce and local vendors. Family friendly.",
            link=None,
        ),
        Event(
            title="New Haven Museum: Curator Talk",
            start=base_date + timedelta(days=3),
            end=None,
            location="114 Whitney Ave, New Haven",
            category="Arts & Culture",
            description="Behind-the-scenes talk on the latest exhibit.",
            link=None,
        ),
        Event(
            title="Concert on the Green",
            start=base_date.replace(hour=19) + timedelta(days=4),
            end=None,
            location="New Haven Green",
            category="Music",
            description="Free outdoor concert series; bring a blanket or chair.",
            link=None,
        ),
        Event(
            title="East Rock Hike & Cleanup",
            start=base_date.replace(hour=9) + timedelta(days=2),
            end=None,
            location="East Rock Park",
            category="Outdoors",
            description="Community hike followed by a short park cleanup.",
            link=None,
        ),
        Event(
            title="Science Café: Climate & Coastlines",
            start=base_date.replace(hour=18) + timedelta(days=6),
            end=None,
            location="Downtown Café",
            category="Talk",
            description="Informal discussion with local scientists; open to all.",
            link=None,
        ),
    ]
    return events[:max_events]


