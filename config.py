import os
from typing import List


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
            "https://ctmirror.org/feed/,https://www.nhregister.com/news/local/rss,https://www.ctinsider.com/news/new-haven/rss/",
        ).split(",")
        if url.strip()
    ]
    RSS_PER_FEED_LIMIT: int = int(os.getenv("RSS_PER_FEED_LIMIT", "5"))
    RSS_OVERALL_LIMIT: int = int(os.getenv("RSS_OVERALL_LIMIT", "20"))

    # Weather (New Haven, CT defaults)
    WEATHER_LAT: float = float(os.getenv("WEATHER_LAT", "41.3083"))
    WEATHER_LON: float = float(os.getenv("WEATHER_LON", "-72.9279"))

    # Networking and caching
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "5"))
    CACHE_TTL_RSS_SECONDS: int = int(os.getenv("CACHE_TTL_RSS_SECONDS", "600"))
    CACHE_TTL_WEATHER_SECONDS: int = int(os.getenv("CACHE_TTL_WEATHER_SECONDS", "900"))

    # Flask
    DEBUG: bool = _get_bool("FLASK_DEBUG", False)


