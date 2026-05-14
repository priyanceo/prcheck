"""Tests for src/label_staleness.py."""
from datetime import datetime, timedelta, timezone

import pytest

from src.label_staleness import (
    StaleLabelEntry,
    StalenessReport,
    build_staleness_report,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TestStaleLabelEntry:
    def test_is_stale_when_old(self):
        applied = _now() - timedelta(days=35)
        entry = StaleLabelEntry(label="bug", applied_at=applied, stale_after_days=30)
        assert entry.is_stale is True

    def test_not_stale_when_recent(self):
        applied = _now() - timedelta(days=5)
        entry = StaleLabelEntry(label="bug", applied_at=applied, stale_after_days=30)
        assert entry.is_stale is False

    def test_stale_on_exact_boundary(self):
        applied = _now() - timedelta(days=30)
        entry = StaleLabelEntry(label="bug", applied_at=applied, stale_after_days=30)
        assert entry.is_stale is True

    def test_to_dict_keys(self):
        applied = _now()
        entry = StaleLabelEntry(label="wip", applied_at=applied, stale_after_days=7)
        d = entry.to_dict()
        assert set(d.keys()) == {"label", "applied_at", "stale_after_days", "is_stale"}

    def test_to_dict_values(self):
        applied = _now() - timedelta(days=10)
        entry = StaleLabelEntry(label="wip", applied_at=applied, stale_after_days=7)
        d = entry.to_dict()
        assert d["label"] == "wip"
        assert d["is_stale"] is True


class TestStalenessReport:
    def _make_entry(self, days_old: int, stale_after: int = 30) -> StaleLabelEntry:
        return StaleLabelEntry(
            label="x",
            applied_at=_now() - timedelta(days=days_old),
            stale_after_days=stale_after,
        )

    def test_has_stale_false_when_empty(self):
        r = StalenessReport(pr_number=1, repo="o/r")
        assert r.has_stale is False

    def test_record_routes_stale_entry(self):
        r = StalenessReport(pr_number=1, repo="o/r")
        r.record(self._make_entry(days_old=40, stale_after=30))
        assert len(r.stale) == 1
        assert len(r.fresh) == 0

    def test_record_routes_fresh_entry(self):
        r = StalenessReport(pr_number=1, repo="o/r")
        r.record(self._make_entry(days_old=5, stale_after=30))
        assert len(r.fresh) == 1
        assert len(r.stale) == 0

    def test_to_dict_keys(self):
        r = StalenessReport(pr_number=42, repo="org/repo")
        d = r.to_dict()
        assert set(d.keys()) == {"pr_number", "repo", "stale", "fresh"}


class TestBuildStalenessReport:
    def test_empty_labels_returns_empty_report(self):
        r = build_staleness_report(1, "o/r", [])
        assert not r.has_stale
        assert r.fresh == []

    def test_stale_label_detected(self):
        old_date = (_now() - timedelta(days=60)).isoformat()
        r = build_staleness_report(1, "o/r", [{"label": "bug", "applied_at": old_date}])
        assert r.has_stale
        assert r.stale[0].label == "bug"

    def test_per_label_override_respected(self):
        recent = (_now() - timedelta(days=10)).isoformat()
        r = build_staleness_report(
            1, "o/r",
            [{"label": "wip", "applied_at": recent, "stale_after_days": 7}],
        )
        assert r.has_stale

    def test_naive_datetime_treated_as_utc(self):
        naive = (datetime.utcnow() - timedelta(days=5)).isoformat()
        r = build_staleness_report(1, "o/r", [{"label": "x", "applied_at": naive}])
        assert len(r.fresh) == 1
