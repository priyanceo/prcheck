"""Tests for src/label_history.py"""
import json
from pathlib import Path

import pytest

from src.label_history import LabelEvent, LabelHistory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def history_path(tmp_path: Path) -> Path:
    return tmp_path / "history" / "labels.jsonl"


@pytest.fixture
def history(history_path: Path) -> LabelHistory:
    return LabelHistory(history_path)


# ---------------------------------------------------------------------------
# LabelEvent
# ---------------------------------------------------------------------------

class TestLabelEvent:
    def test_to_dict_contains_expected_keys(self):
        event = LabelEvent(label="bug", action="added", reason="path match", run_id="42")
        d = event.to_dict()
        assert set(d.keys()) == {"label", "action", "reason", "run_id", "timestamp"}

    def test_to_dict_values(self):
        event = LabelEvent(label="bug", action="added", reason="path match", run_id="42", timestamp="ts")
        d = event.to_dict()
        assert d["label"] == "bug"
        assert d["action"] == "added"
        assert d["reason"] == "path match"
        assert d["run_id"] == "42"
        assert d["timestamp"] == "ts"

    def test_from_dict_round_trip(self):
        original = LabelEvent(label="feat", action="removed", reason="conflict", run_id="7", timestamp="t")
        restored = LabelEvent.from_dict(original.to_dict())
        assert restored.label == original.label
        assert restored.action == original.action
        assert restored.run_id == original.run_id
        assert restored.timestamp == original.timestamp


# ---------------------------------------------------------------------------
# LabelHistory.record
# ---------------------------------------------------------------------------

class TestLabelHistoryRecord:
    def test_creates_file_on_first_record(self, history: LabelHistory, history_path: Path):
        history.record(LabelEvent(label="bug", action="added", reason="r", run_id="1"))
        assert history_path.exists()

    def test_appends_valid_json_lines(self, history: LabelHistory, history_path: Path):
        history.record(LabelEvent(label="bug", action="added", reason="r", run_id="1"))
        history.record(LabelEvent(label="feat", action="removed", reason="c", run_id="2"))
        lines = history_path.read_text().strip().splitlines()
        assert len(lines) == 2
        for line in lines:
            json.loads(line)  # must be valid JSON

    def test_all_events_returns_recorded(self, history: LabelHistory):
        history.record(LabelEvent(label="bug", action="added", reason="r", run_id="1"))
        assert len(history.all_events()) == 1


# ---------------------------------------------------------------------------
# LabelHistory queries
# ---------------------------------------------------------------------------

class TestLabelHistoryQueries:
    def test_events_for_label_filters_correctly(self, history: LabelHistory):
        history.record(LabelEvent(label="bug", action="added", reason="r", run_id="1"))
        history.record(LabelEvent(label="feat", action="added", reason="r", run_id="2"))
        history.record(LabelEvent(label="bug", action="removed", reason="c", run_id="3"))
        assert len(history.events_for_label("bug")) == 2
        assert len(history.events_for_label("feat")) == 1

    def test_last_action_for_label_returns_latest(self, history: LabelHistory):
        history.record(LabelEvent(label="bug", action="added", reason="r", run_id="1"))
        history.record(LabelEvent(label="bug", action="removed", reason="c", run_id="2"))
        last = history.last_action_for_label("bug")
        assert last is not None
        assert last.action == "removed"

    def test_last_action_returns_none_for_unknown_label(self, history: LabelHistory):
        assert history.last_action_for_label("nonexistent") is None

    def test_history_loaded_from_existing_file(self, history_path: Path):
        history_path.parent.mkdir(parents=True, exist_ok=True)
        event = LabelEvent(label="bug", action="added", reason="r", run_id="1", timestamp="t")
        history_path.write_text(json.dumps(event.to_dict()) + "\n")
        reloaded = LabelHistory(history_path)
        assert len(reloaded.all_events()) == 1
        assert reloaded.all_events()[0].label == "bug"
