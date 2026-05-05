"""Simple file-based cache for GitHub API responses to avoid rate limiting."""

import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional


DEFAULT_CACHE_DIR = Path(".prcheck_cache")
DEFAULT_TTL_SECONDS = 300  # 5 minutes


class ResponseCache:
    """Caches API responses on disk with TTL-based expiration."""

    def __init__(
        self,
        cache_dir: Path = DEFAULT_CACHE_DIR,
        ttl: int = DEFAULT_TTL_SECONDS,
    ) -> None:
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _key_path(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{digest}.json"

    def get(self, key: str) -> Optional[Any]:
        """Return cached value or None if missing / expired."""
        path = self._key_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            return None
        if time.time() - data["timestamp"] > self.ttl:
            path.unlink(missing_ok=True)
            return None
        return data["value"]

    def set(self, key: str, value: Any) -> None:
        """Persist a value under *key*."""
        path = self._key_path(key)
        payload = {"timestamp": time.time(), "value": value}
        path.write_text(json.dumps(payload))

    def invalidate(self, key: str) -> None:
        """Remove a single cache entry if it exists."""
        self._key_path(key).unlink(missing_ok=True)

    def clear(self) -> None:
        """Delete all cache entries."""
        for entry in self.cache_dir.glob("*.json"):
            entry.unlink(missing_ok=True)
