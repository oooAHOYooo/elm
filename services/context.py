"""
Contextual intelligence service for Elm City Daily.

Provides automatic, time-aware, and condition-based information
to make the dashboard immediately useful without user interaction.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo
import math

_logger = logging.getLogger(__name__)

# New Haven coordinates
NH_LAT = 41.3083
NH_LON = -72.9279
TZ = ZoneInfo("America/New_York")


def get_time_context(now: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Get contextual information based on current time.
    Returns greeting, time period, and relevant tips.
    """
    if now is None:
        now = datetime.now(TZ)
    
    hour = now.hour
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    is_weekend = weekday >= 5
    
    # Determine time period and greeting
    if 5 <= hour < 12:
        period = "morning"
        greeting = "Good morning"
        icon = "🌅"
    elif 12 <= hour < 17:
        period = "afternoon"
        greeting = "Good afternoon"
        icon = "☀️"
    elif 17 <= hour < 21:
        period = "evening"
        greeting = "Good evening"
        icon = "🌆"
    else:
        period = "night"
        greeting = "Good evening"
        icon = "🌙"
    
    # Day type
    if is_weekend:
        day_type = "weekend"
        day_emoji = "🎉"
    else:
        day_type = "weekday"
        day_emoji = "💼"
    
    # Rush hour detection
    is_rush_hour = not is_weekend and (
        (7 <= hour <= 9) or (16 <= hour <= 18)
    )
    
    return {
        "greeting": greeting,
        "icon": icon,
        "period": period,
        "hour": hour,
        "is_weekend": is_weekend,
        "is_rush_hour": is_rush_hour,
        "day_type": day_type,
        "day_emoji": day_emoji,
        "day_name": now.strftime("%A"),
        "date_short": now.strftime("%b %d"),
    }


def calculate_sun_times(
    date: Optional[datetime] = None,
    lat: float = NH_LAT,
    lon: float = NH_LON
) -> Dict[str, str]:
    """
    Calculate approximate sunrise and sunset times for New Haven.
    Uses a simplified algorithm (accurate to ~5 minutes).
    """
    if date is None:
        date = datetime.now(TZ)
    
    # Day of year
    day_of_year = date.timetuple().tm_yday
    
    # Approximate solar noon (in hours, UTC)
    # longitude correction: 4 minutes per degree
    lng_hour = lon / 15
    
    # Approximate time of sunrise/sunset
    # Using simplified equation
    
    # Calculate the Sun's declination
    # Simplified formula
    declination = 23.45 * math.sin(math.radians((360 / 365) * (day_of_year - 81)))
    
    # Hour angle
    lat_rad = math.radians(lat)
    decl_rad = math.radians(declination)
    
    try:
        cos_hour_angle = -math.tan(lat_rad) * math.tan(decl_rad)
        # Clamp to valid range
        cos_hour_angle = max(-1, min(1, cos_hour_angle))
        hour_angle = math.degrees(math.acos(cos_hour_angle))
    except ValueError:
        # Polar day/night edge case
        hour_angle = 90
    
    # Sunrise and sunset in hours (local solar time)
    solar_noon = 12 - lng_hour + (date.utcoffset().total_seconds() / 3600 if date.utcoffset() else -5)
    sunrise_hour = solar_noon - (hour_angle / 15)
    sunset_hour = solar_noon + (hour_angle / 15)
    
    # Apply equation of time correction (simplified)
    b = math.radians((360 / 365) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    eot_hours = eot / 60
    
    sunrise_hour -= eot_hours
    sunset_hour -= eot_hours
    
    def hours_to_time_str(h: float) -> str:
        hours = int(h)
        minutes = int((h - hours) * 60)
        dt = datetime(2000, 1, 1, hours % 24, minutes)
        return dt.strftime("%I:%M %p").lstrip("0")
    
    # Calculate day length
    day_length_hours = sunset_hour - sunrise_hour
    day_length_h = int(day_length_hours)
    day_length_m = int((day_length_hours - day_length_h) * 60)
    
    return {
        "sunrise": hours_to_time_str(sunrise_hour),
        "sunset": hours_to_time_str(sunset_hour),
        "day_length": f"{day_length_h}h {day_length_m}m",
        "solar_noon": hours_to_time_str(solar_noon),
    }


def get_smart_tips(
    weather: Optional[Dict[str, Any]] = None,
    air_quality: Optional[Dict[str, Any]] = None,
    time_ctx: Optional[Dict[str, Any]] = None,
    now: Optional[datetime] = None,
) -> List[Dict[str, str]]:
    """
    Generate smart, contextual tips based on current conditions.
    Returns list of {icon, tip, priority} dicts.
    """
    if now is None:
        now = datetime.now(TZ)
    if time_ctx is None:
        time_ctx = get_time_context(now)
    
    tips = []
    
    # Weather-based tips
    if weather:
        temp = weather.get("current_temp")
        precip = weather.get("precip_probability")
        desc = (weather.get("weather_desc") or "").lower()
        
        # Temperature tips
        if temp is not None:
            if temp <= 32:
                tips.append({
                    "icon": "🥶",
                    "tip": "Freezing temps — watch for ice on roads and sidewalks",
                    "priority": "high"
                })
            elif temp <= 40:
                tips.append({
                    "icon": "🧥",
                    "tip": "Bundle up! It's cold outside",
                    "priority": "medium"
                })
            elif temp >= 90:
                tips.append({
                    "icon": "🥵",
                    "tip": "Heat advisory — stay hydrated, limit outdoor exertion",
                    "priority": "high"
                })
            elif temp >= 80:
                tips.append({
                    "icon": "💧",
                    "tip": "Hot day — drink plenty of water",
                    "priority": "medium"
                })
        
        # Precipitation tips
        if precip is not None and precip > 50:
            tips.append({
                "icon": "☔",
                "tip": f"{precip}% chance of precipitation — bring an umbrella",
                "priority": "high"
            })
        elif precip is not None and precip > 30:
            tips.append({
                "icon": "🌂",
                "tip": "Rain possible — consider bringing an umbrella",
                "priority": "medium"
            })
        
        # Weather condition tips
        if "snow" in desc:
            tips.append({
                "icon": "❄️",
                "tip": "Snow expected — check parking bans and allow extra travel time",
                "priority": "high"
            })
        elif "thunder" in desc or "storm" in desc:
            tips.append({
                "icon": "⛈️",
                "tip": "Thunderstorms expected — avoid outdoor activities",
                "priority": "high"
            })
        elif "fog" in desc:
            tips.append({
                "icon": "🌫️",
                "tip": "Foggy conditions — drive carefully with low beams",
                "priority": "medium"
            })
    
    # Air quality tips
    if air_quality and air_quality.get("available"):
        aqi = air_quality.get("aqi")
        if aqi is not None:
            if aqi > 150:
                tips.append({
                    "icon": "😷",
                    "tip": "Unhealthy air quality — limit outdoor activities",
                    "priority": "high"
                })
            elif aqi > 100:
                tips.append({
                    "icon": "🌬️",
                    "tip": "Air quality moderate — sensitive groups should limit outdoor exertion",
                    "priority": "medium"
                })
    
    # Time-based tips
    if time_ctx:
        if time_ctx.get("is_rush_hour"):
            tips.append({
                "icon": "🚗",
                "tip": "Rush hour — expect traffic on I-95 and downtown",
                "priority": "low"
            })
        
        # Weekend tips
        if time_ctx.get("is_weekend"):
            if time_ctx.get("period") == "morning":
                tips.append({
                    "icon": "🥐",
                    "tip": "Weekend morning — farmers markets may be open!",
                    "priority": "low"
                })
    
    # Day-specific tips
    weekday = now.weekday()
    
    # Monday tips
    if weekday == 0:
        tips.append({
            "icon": "🗑️",
            "tip": "Check your trash/recycling pickup schedule",
            "priority": "low"
        })
    
    # Friday tips
    if weekday == 4 and time_ctx and time_ctx.get("period") in ("afternoon", "evening"):
        tips.append({
            "icon": "🎶",
            "tip": "TGIF! Check local venues for live music tonight",
            "priority": "low"
        })
    
    # Sort by priority
    priority_order = {"high": 0, "medium": 1, "low": 2}
    tips.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
    
    return tips[:4]  # Return top 4 tips


def get_today_summary(
    weather: Optional[Dict[str, Any]] = None,
    events_count: int = 0,
    alerts_count: int = 0,
    air_quality: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a "Today at a Glance" summary.
    """
    now = datetime.now(TZ)
    time_ctx = get_time_context(now)
    sun_times = calculate_sun_times(now)
    tips = get_smart_tips(weather, air_quality, time_ctx, now)
    
    # Build summary items
    summary_items = []
    
    # Weather summary
    if weather:
        temp = weather.get("current_temp")
        high = weather.get("high_temp")
        low = weather.get("low_temp")
        desc = weather.get("weather_desc", "")
        icon = weather.get("weather_icon", "")
        
        if temp is not None:
            weather_text = f"{icon} {int(temp)}°F"
            if high and low:
                weather_text += f" (H:{int(high)}° L:{int(low)}°)"
            if desc:
                weather_text += f" — {desc}"
            summary_items.append({
                "type": "weather",
                "text": weather_text,
            })
    
    # Sun times
    summary_items.append({
        "type": "sun",
        "text": f"🌅 {sun_times['sunrise']} → 🌇 {sun_times['sunset']} ({sun_times['day_length']})",
    })
    
    # Events
    if events_count > 0:
        summary_items.append({
            "type": "events",
            "text": f"📅 {events_count} event{'s' if events_count != 1 else ''} happening this week",
        })
    
    # Alerts
    if alerts_count > 0:
        summary_items.append({
            "type": "alerts",
            "text": f"⚠️ {alerts_count} active weather alert{'s' if alerts_count != 1 else ''}",
        })
    
    # Air quality
    if air_quality and air_quality.get("available"):
        aqi = air_quality.get("aqi")
        category = air_quality.get("category", "")
        emoji = air_quality.get("emoji", "")
        if aqi:
            summary_items.append({
                "type": "aqi",
                "text": f"{emoji} AQI {aqi} — {category}",
            })
    
    return {
        "time_context": time_ctx,
        "sun_times": sun_times,
        "summary_items": summary_items,
        "tips": tips,
        "generated_at": now.isoformat(),
    }


def get_holiday_info(date: Optional[datetime] = None) -> Optional[Dict[str, str]]:
    """
    Check if today is a notable holiday or observance.
    Returns None if not a holiday.
    """
    if date is None:
        date = datetime.now(TZ)
    
    month = date.month
    day = date.day
    weekday = date.weekday()
    
    # Fixed holidays
    fixed_holidays = {
        (1, 1): {"name": "New Year's Day", "icon": "🎆", "type": "federal"},
        (7, 4): {"name": "Independence Day", "icon": "🇺🇸", "type": "federal"},
        (12, 25): {"name": "Christmas Day", "icon": "🎄", "type": "federal"},
        (12, 31): {"name": "New Year's Eve", "icon": "🥂", "type": "observance"},
        (2, 14): {"name": "Valentine's Day", "icon": "❤️", "type": "observance"},
        (3, 17): {"name": "St. Patrick's Day", "icon": "☘️", "type": "observance"},
        (10, 31): {"name": "Halloween", "icon": "🎃", "type": "observance"},
        (11, 11): {"name": "Veterans Day", "icon": "🎖️", "type": "federal"},
        (6, 19): {"name": "Juneteenth", "icon": "✊", "type": "federal"},
    }
    
    if (month, day) in fixed_holidays:
        return fixed_holidays[(month, day)]
    
    # Floating holidays (simplified)
    # MLK Day: 3rd Monday of January
    if month == 1 and weekday == 0 and 15 <= day <= 21:
        return {"name": "Martin Luther King Jr. Day", "icon": "✊", "type": "federal"}
    
    # Presidents Day: 3rd Monday of February
    if month == 2 and weekday == 0 and 15 <= day <= 21:
        return {"name": "Presidents Day", "icon": "🏛️", "type": "federal"}
    
    # Memorial Day: Last Monday of May
    if month == 5 and weekday == 0 and day >= 25:
        return {"name": "Memorial Day", "icon": "🪖", "type": "federal"}
    
    # Labor Day: 1st Monday of September
    if month == 9 and weekday == 0 and day <= 7:
        return {"name": "Labor Day", "icon": "👷", "type": "federal"}
    
    # Columbus/Indigenous Peoples' Day: 2nd Monday of October
    if month == 10 and weekday == 0 and 8 <= day <= 14:
        return {"name": "Indigenous Peoples' Day", "icon": "🌎", "type": "federal"}
    
    # Thanksgiving: 4th Thursday of November
    if month == 11 and weekday == 3 and 22 <= day <= 28:
        return {"name": "Thanksgiving", "icon": "🦃", "type": "federal"}
    
    return None

