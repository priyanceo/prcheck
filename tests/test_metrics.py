"""Unit tests for src/metrics.py."""
from __future__ import annotations

import time

import pytest

from src.metrics import RunMetrics, format_summary


class TestRunMetrics:
    def test_initial_state(self):
        m = RunMetrics(pr_number=42)
        assert m.pr_number == 42
        assert m.labels_added == []
        assert m.labels_removed == []
        assert m.files_evaluated == 0
        assert m.total_changes == 0
        assert m.end_time is None
        assert m.elapsed_seconds is None

    def test_finish_records_end_time(self):
        m = RunMetrics(pr_number=1)
        before = time.monotonic()
        m.finish()
        after = time.monotonic()
        assert m.end_time is not None
        assert before <= m.end_time <= after

    def test_elapsed_seconds_after_finish(self):
        m = RunMetrics(pr_number=1)
        time.sleep(0.01)
        m.finish()
        assert m.elapsed_seconds is not None
        assert m.elapsed_seconds >= 0.0

    def test_to_dict_keys(self):
        m = RunMetrics(pr_number=7, files_evaluated=3, total_changes=50)
        m.labels_added = ["bug"]
        m.labels_removed = ["wip"]
        m.finish()
        d = m.to_dict()
        assert d["pr_number"] == 7
        assert d["files_evaluated"] == 3
        assert d["total_changes"] == 50
        assert d["labels_added"] == ["bug"]
        assert d["labels_removed"] == ["wip"]
        assert d["elapsed_seconds"] is not None

    def test_to_dict_labels_are_copies(self):
        m = RunMetrics(pr_number=1)
        m.labels_added = ["x"]
        d = m.to_dict()
        d["labels_added"].append("y")
        assert m.labels_added == ["x"]


class TestFormatSummary:
    def test_contains_pr_number(self):
        m = RunMetrics(pr_number=99)
        m.finish()
        assert "#99" in format_summary(m)

    def test_no_labels_shows_none(self):
        m = RunMetrics(pr_number=1)
        m.finish()
        summary = format_summary(m)
        assert "added=[none]" in summary
        assert "removed=[none]" in summary

    def test_labels_shown(self):
        m = RunMetrics(pr_number=2)
        m.labels_added = ["size/large"]
        m.labels_removed = ["size/small"]
        m.finish()
        summary = format_summary(m)
        assert "size/large" in summary
        assert "size/small" in summary

    def test_elapsed_na_when_not_finished(self):
        m = RunMetrics(pr_number=3)
        assert "n/a" in format_summary(m)
