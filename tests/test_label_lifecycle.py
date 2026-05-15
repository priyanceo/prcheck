"""Tests for LabelLifecycleStore and LifecycleEvent."""
import json
from pathlib import Path

import pytest

from src.label_lifecycle import LifecycleEvent, LabelLifecycleStore


@pytest.fixture
def store_path(tmp_path: Path) -> Path:
    return tmp_path / "lifecycle.jsonl"


@pytest.fixture
def store(store_path: Path) -> LabelLifecycleStore:
    return LabelLifecycleStore(store_path)


class TestLifecycleEvent:
    def test_to_dict_contains_expected_keys(self):
        evt = LifecycleEvent(label="bug", event="created", pr_number=42)
        d = evt.to_dict()
        assert set(d.keys()) == {"label", "event", "timestamp", "pr_number"}

    def test_to_dict_values(self):
        evt = LifecycleEvent(label="bug", event="removed", pr_number=7)
        d = evt.to_dict()
        assert d["label"] == "bug"
        assert d["event"] == "removed"
        assert d["pr_number"] == 7

    def test_from_dict_roundtrip(self):
        evt = LifecycleEvent(label="feat", event="updated", pr_number=1)
        restored = LifecycleEvent.from_dict(evt.to_dict())
        assert restored.label == evt.label
        assert restored.event == evt.event
        assert restored.pr_number == evt.pr_number


class TestLabelLifecycleStoreRecord:
    def test_record_returns_event(self, store: LabelLifecycleStore):
        evt = store.record("bug", "created", pr_number=1)
        assert evt.label == "bug"
        assert evt.event == "created"

    def test_record_invalid_event_raises(self, store: LabelLifecycleStore):
        with pytest.raises(ValueError, match="Unknown lifecycle event"):
            store.record("bug", "reopen")

    def test_record_persists_to_file(self, store: LabelLifecycleStore, store_path: Path):
        store.record("fix", "created", pr_number=5)
        lines = store_path.read_text().splitlines()
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["label"] == "fix"

    def test_multiple_records_appended(self, store: LabelLifecycleStore, store_path: Path):
        store.record("bug", "created")
        store.record("bug", "removed")
        lines = store_path.read_text().splitlines()
        assert len(lines) == 2


class TestLabelLifecycleStoreQuery:
    def test_events_for_returns_matching(self, store: LabelLifecycleStore):
        store.record("bug", "created")
        store.record("feat", "created")
        evts = store.events_for("bug")
        assert len(evts) == 1
        assert evts[0].label == "bug"

    def test_events_for_empty_when_no_match(self, store: LabelLifecycleStore):
        store.record("bug", "created")
        assert store.events_for("unknown") == []

    def test_latest_event_returns_last(self, store: LabelLifecycleStore):
        store.record("bug", "created")
        store.record("bug", "updated")
        latest = store.latest_event("bug")
        assert latest is not None
        assert latest.event == "updated"

    def test_latest_event_none_when_missing(self, store: LabelLifecycleStore):
        assert store.latest_event("ghost") is None

    def test_reload_from_disk(self, store_path: Path):
        s1 = LabelLifecycleStore(store_path)
        s1.record("bug", "created", pr_number=3)
        s2 = LabelLifecycleStore(store_path)
        assert len(s2.all_events()) == 1
        assert s2.all_events()[0].label == "bug"
