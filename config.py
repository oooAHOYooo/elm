import os
from typing import List
from datetime import timedelta


def _get_bool(env_key: str, default: bool = False) -> bool:
    value = os.getenv(env_key)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


class Config:
    APP_NAME: str = os.getenv("APP_NAME", "Elm City Daily")

    # RSS
    FEED_URLS: List[str] = [
        url.strip()
        for url in os.getenv(
            "FEED_URLS",
            # Defaults favor reliable sources; omit endpoints returning 404/403.
            "https://ctmirror.org/feed/",
        ).split(",")
        if url.strip()
    ]
    RSS_PER_FEED_LIMIT: int = int(os.getenv("RSS_PER_FEED_LIMIT", "5"))
    RSS_OVERALL_LIMIT: int = int(os.getenv("RSS_OVERALL_LIMIT", "20"))

    # Weather (New Haven, CT defaults)
    WEATHER_LAT: float = float(os.getenv("WEATHER_LAT", "41.3083"))
    WEATHER_LON: float = float(os.getenv("WEATHER_LON", "-72.9279"))

    # Networking and caching
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "5"))  # 5 seconds for reliability (was 3s)
    CACHE_TTL_RSS_SECONDS: int = int(os.getenv("CACHE_TTL_RSS_SECONDS", "600"))
    CACHE_TTL_WEATHER_SECONDS: int = int(os.getenv("CACHE_TTL_WEATHER_SECONDS", "900"))

    # Air Quality (AirNow API - free key from https://docs.airnowapi.org/)
    AIRNOW_API_KEY: str = os.getenv("AIRNOW_API_KEY", "")

    # Flask
    DEBUG: bool = _get_bool("FLASK_DEBUG", False)
    # Cache static assets (CSS/JS/images) for faster repeat loads
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(days=7)


