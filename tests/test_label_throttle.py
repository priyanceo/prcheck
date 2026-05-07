"""Tests for src/label_throttle.py"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from src.label_throttle import LabelThrottle, ThrottleConfig


@pytest.fixture()
def store(tmp_path: Path) -> Path:
    return tmp_path / "throttle.json"


@pytest.fixture()
def throttle(store: Path) -> LabelThrottle:
    cfg = ThrottleConfig(window_seconds=60, max_operations=3)
    return LabelThrottle(store, cfg)


class TestIsAllowed:
    def test_allowed_when_no_history(self, throttle: LabelThrottle) -> None:
        assert throttle.is_allowed("bug") is True

    def test_allowed_below_limit(self, throttle: LabelThrottle) -> None:
        throttle.record_operation("bug")
        throttle.record_operation("bug")
        assert throttle.is_allowed("bug") is True

    def test_blocked_at_limit(self, throttle: LabelThrottle) -> None:
        for _ in range(3):
            throttle.record_operation("bug")
        assert throttle.is_allowed("bug") is False

    def test_different_labels_are_independent(self, throttle: LabelThrottle) -> None:
        for _ in range(3):
            throttle.record_operation("bug")
        assert throttle.is_allowed("feature") is True

    def test_expired_timestamps_not_counted(self, store: Path) -> None:
        old_ts = time.time() - 120  # older than 60 s window
        store.write_text(json.dumps({"bug": [old_ts, old_ts, old_ts]}))
        cfg = ThrottleConfig(window_seconds=60, max_operations=3)
        t = LabelThrottle(store, cfg)
        assert t.is_allowed("bug") is True


class TestRemaining:
    def test_full_remaining_when_empty(self, throttle: LabelThrottle) -> None:
        assert throttle.remaining("bug") == 3

    def test_decrements_after_operation(self, throttle: LabelThrottle) -> None:
        throttle.record_operation("bug")
        assert throttle.remaining("bug") == 2

    def test_zero_when_exhausted(self, throttle: LabelThrottle) -> None:
        for _ in range(3):
            throttle.record_operation("bug")
        assert throttle.remaining("bug") == 0


class TestPersistence:
    def test_state_reloaded_across_instances(self, store: Path) -> None:
        cfg = ThrottleConfig(window_seconds=60, max_operations=3)
        t1 = LabelThrottle(store, cfg)
        t1.record_operation("bug")
        t1.record_operation("bug")

        t2 = LabelThrottle(store, cfg)
        assert t2.remaining("bug") == 1

    def test_store_created_on_first_record(self, store: Path) -> None:
        cfg = ThrottleConfig(window_seconds=60, max_operations=3)
        t = LabelThrottle(store, cfg)
        assert not store.exists()
        t.record_operation("bug")
        assert store.exists()

    def test_missing_store_does_not_raise(self, store: Path) -> None:
        cfg = ThrottleConfig(window_seconds=60, max_operations=3)
        t = LabelThrottle(store, cfg)  # store absent — should not raise
        assert t.remaining("bug") == 3
