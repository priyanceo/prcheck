"""Tests for src/cache.py"""

import json
import time
from pathlib import Path

import pytest

from src.cache import ResponseCache


@pytest.fixture()
def cache(tmp_path: Path) -> ResponseCache:
    return ResponseCache(cache_dir=tmp_path / "cache", ttl=60)


class TestResponseCacheGet:
    def test_returns_none_for_missing_key(self, cache: ResponseCache) -> None:
        assert cache.get("nonexistent") is None

    def test_returns_stored_value(self, cache: ResponseCache) -> None:
        cache.set("k", {"files": ["a.py"]})
        assert cache.get("k") == {"files": ["a.py"]}

    def test_returns_none_after_ttl_expires(self, tmp_path: Path) -> None:
        short_cache = ResponseCache(cache_dir=tmp_path / "c", ttl=1)
        short_cache.set("k", "value")
        time.sleep(1.1)
        assert short_cache.get("k") is None

    def test_returns_none_for_corrupt_entry(self, cache: ResponseCache) -> None:
        key_path = cache._key_path("bad")
        cache.cache_dir.mkdir(parents=True, exist_ok=True)
        key_path.write_text("not-json")
        assert cache.get("bad") is None


class TestResponseCacheSet:
    def test_creates_cache_file(self, cache: ResponseCache) -> None:
        cache.set("repo/123", ["label-a"])
        path = cache._key_path("repo/123")
        assert path.exists()

    def test_stored_payload_has_timestamp(self, cache: ResponseCache) -> None:
        cache.set("k", 42)
        data = json.loads(cache._key_path("k").read_text())
        assert "timestamp" in data
        assert data["value"] == 42


class TestResponseCacheInvalidate:
    def test_removes_existing_entry(self, cache: ResponseCache) -> None:
        cache.set("k", "v")
        cache.invalidate("k")
        assert cache.get("k") is None

    def test_noop_for_missing_key(self, cache: ResponseCache) -> None:
        cache.invalidate("never-set")  # should not raise


class TestResponseCacheClear:
    def test_removes_all_entries(self, cache: ResponseCache) -> None:
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_clear_on_empty_cache_does_not_raise(self, cache: ResponseCache) -> None:
        cache.clear()  # should not raise
