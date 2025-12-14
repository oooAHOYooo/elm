import time
import pickle
import os
import logging
from typing import Any, Dict, Optional, Tuple

_logger = logging.getLogger(__name__)

class TTLCache:
    """
    In-memory TTL cache with optional file persistence.
    """

    def __init__(self, ttl_seconds: int = 600, filepath: Optional[str] = None):
        self.ttl_seconds = ttl_seconds
        self.filepath = filepath
        self._store: Dict[str, Tuple[float, Any]] = {}
        
        if self.filepath and os.path.exists(self.filepath):
            self._load()

    def _load(self) -> None:
        try:
            with open(self.filepath, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict):
                    # Prune expired on load
                    now = time.time()
                    self._store = {
                        k: v for k, v in data.items() 
                        if now - v[0] <= self.ttl_seconds
                    }
        except Exception as e:
            _logger.warning(f"Failed to load cache from {self.filepath}: {e}")
            self._store = {}

    def _save(self) -> None:
        if not self.filepath:
            return
        try:
            # Prune before saving to keep file small
            now = time.time()
            self._store = {
                k: v for k, v in self._store.items() 
                if now - v[0] <= self.ttl_seconds
            }
            with open(self.filepath, "wb") as f:
                pickle.dump(self._store, f)
        except Exception as e:
            _logger.warning(f"Failed to save cache to {self.filepath}: {e}")

    def get(self, key: str) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if time.time() - ts > self.ttl_seconds:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.time(), value)
        # Auto-save on set if persistent
        if self.filepath:
            self._save()

    def clear(self) -> None:
        self._store.clear()
        if self.filepath:
            if os.path.exists(self.filepath):
                try:
                    os.remove(self.filepath)
                except Exception:
                    pass
