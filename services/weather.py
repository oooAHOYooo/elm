import logging
import time
from typing import Any, Dict, Optional

import requests

_logger = logging.getLogger(__name__)

_WEATHER_CACHE: Dict[str, Any] = {
    "timestamp": 0.0,
    "data": None,
}

# Mapping for Open-Meteo weather codes
_WEATHER_CODE_MAP: Dict[int, Dict[str, str]] = {
    0: {"desc": "Clear sky", "icon": "☀️"},
    1: {"desc": "Mainly clear", "icon": "🌤️"},
    2: {"desc": "Partly cloudy", "icon": "⛅"},
    3: {"desc": "Overcast", "icon": "☁️"},
    45: {"desc": "Fog", "icon": "🌫️"},
    48: {"desc": "Depositing rime fog", "icon": "🌫️"},
    51: {"desc": "Light drizzle", "icon": "🌦️"},
    53: {"desc": "Moderate drizzle", "icon": "🌦️"},
    55: {"desc": "Dense drizzle", "icon": "🌧️"},
    61: {"desc": "Slight rain", "icon": "🌧️"},
    63: {"desc": "Moderate rain", "icon": "🌧️"},
    65: {"desc": "Heavy rain", "icon": "🌧️"},
    71: {"desc": "Slight snow", "icon": "🌨️"},
    73: {"desc": "Moderate snow", "icon": "🌨️"},
    75: {"desc": "Heavy snow", "icon": "❄️"},
    80: {"desc": "Rain showers", "icon": "🌦️"},
    81: {"desc": "Heavy rain showers", "icon": "🌧️"},
    82: {"desc": "Violent rain showers", "icon": "⛈️"},
    95: {"desc": "Thunderstorm", "icon": "⛈️"},
    96: {"desc": "Thunderstorm w/ hail", "icon": "⛈️"},
    99: {"desc": "Thunderstorm w/ heavy hail", "icon": "⛈️"},
}


def _map_code(code: Optional[int]) -> Dict[str, str]:
    if code is None:
        return {"desc": "Unknown", "icon": "ℹ️"}
    return _WEATHER_CODE_MAP.get(code, {"desc": "Unknown", "icon": "ℹ️"})


def fetch_weather(lat: float, lon: float, request_timeout: int = 5) -> Dict[str, Any]:
    """
    Fetch current weather and today's min/max for the given coordinates from Open-Meteo.
    Includes a simple cache to avoid excessive requests.
    """
    now = time.time()
    ttl_seconds = 900  # 15 minutes
    if _WEATHER_CACHE["data"] and now - _WEATHER_CACHE["timestamp"] < ttl_seconds:
        return _WEATHER_CACHE["data"]

    base = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset",
        "temperature_unit": "fahrenheit",
        "timezone": "auto",
    }

    try:
        resp = requests.get(base, params=params, timeout=request_timeout)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current_weather", {})
        daily = data.get("daily", {})

        weather_code = current.get("weathercode")
        mapped = _map_code(weather_code)

        daily_max = None
        daily_min = None
        precip_prob = None
        sunrise = None
        sunset = None
        try:
            daily_max = daily.get("temperature_2m_max", [None])[0]
            daily_min = daily.get("temperature_2m_min", [None])[0]
            precip_prob = daily.get("precipitation_probability_max", [None])[0]
            sunrise = daily.get("sunrise", [None])[0]
            sunset = daily.get("sunset", [None])[0]
        except Exception:
            pass

        result: Dict[str, Any] = {
            "current_temp": current.get("temperature"),
            "wind_speed": current.get("windspeed"),
            "wind_direction": current.get("winddirection"),
            "weather_code": weather_code,
            "weather_desc": mapped["desc"],
            "weather_icon": mapped["icon"],
            "high_temp": daily_max,
            "low_temp": daily_min,
            "precip_probability": precip_prob,
            "sunrise": sunrise,
            "sunset": sunset,
        }

        _WEATHER_CACHE["timestamp"] = now
        _WEATHER_CACHE["data"] = result
        return result
    except Exception as err:
        _logger.error("Failed to fetch weather: %s", err)
        # fallback placeholder if API fails
        return {
            "current_temp": None,
            "wind_speed": None,
            "wind_direction": None,
            "weather_code": None,
            "weather_desc": "Unavailable",
            "weather_icon": "ℹ️",
            "high_temp": None,
            "low_temp": None,
            "precip_probability": None,
        }


