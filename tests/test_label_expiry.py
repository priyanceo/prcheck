"""Tests for src/label_expiry.py."""

import time
from pathlib import Path

import pytest

from src.label_expiry import ExpiryRecord, LabelExpiryStore


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "expiry.jsonl"


@pytest.fixture()
def store(store_path: Path) -> LabelExpiryStore:
    return LabelExpiryStore(store_path)


# ---------------------------------------------------------------------------
# ExpiryRecord
# ---------------------------------------------------------------------------

class TestExpiryRecord:
    def test_is_expired_when_past(self):
        r = ExpiryRecord(label="stale", pr_number=1, expires_at=time.time() - 1)
        assert r.is_expired()

    def test_not_expired_when_future(self):
        r = ExpiryRecord(label="stale", pr_number=1, expires_at=time.time() + 3600)
        assert not r.is_expired()

    def test_to_dict_round_trips(self):
        r = ExpiryRecord(label="bug", pr_number=42, expires_at=9999.0)
        assert ExpiryRecord.from_dict(r.to_dict()) == r

    def test_to_dict_contains_expected_keys(self):
        r = ExpiryRecord(label="bug", pr_number=7, expires_at=1.0)
        assert set(r.to_dict().keys()) == {"label", "pr_number", "expires_at"}


# ---------------------------------------------------------------------------
# LabelExpiryStore
# ---------------------------------------------------------------------------

class TestLabelExpiryStoreSchedule:
    def test_creates_file_on_schedule(self, store: LabelExpiryStore, store_path: Path):
        store.schedule("stale", 1, ttl_seconds=3600)
        assert store_path.exists()

    def test_scheduled_record_is_retrievable(self, store: LabelExpiryStore):
        store.schedule("stale", 1, ttl_seconds=-1)  # already expired
        expired = store.expired_for_pr(1)
        assert len(expired) == 1
        assert expired[0].label == "stale"

    def test_rescheduling_same_label_overwrites(self, store: LabelExpiryStore):
        store.schedule("stale", 1, ttl_seconds=3600)
        store.schedule("stale", 1, ttl_seconds=-1)
        expired = store.expired_for_pr(1)
        assert len(expired) == 1

    def test_non_expired_not_returned(self, store: LabelExpiryStore):
        store.schedule("stale", 1, ttl_seconds=3600)
        assert store.expired_for_pr(1) == []


class TestLabelExpiryStoreRemove:
    def test_remove_deletes_record(self, store: LabelExpiryStore):
        store.schedule("stale", 1, ttl_seconds=-1)
        store.remove("stale", 1)
        assert store.expired_for_pr(1) == []

    def test_remove_nonexistent_is_noop(self, store: LabelExpiryStore):
        store.remove("ghost", 99)  # should not raise

    def test_remove_leaves_other_labels(self, store: LabelExpiryStore):
        store.schedule("stale", 1, ttl_seconds=-1)
        store.schedule("bug", 1, ttl_seconds=-1)
        store.remove("stale", 1)
        expired = store.expired_for_pr(1)
        assert len(expired) == 1
        assert expired[0].label == "bug"
