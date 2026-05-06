"""Tests for src/dry_run.py"""
import pytest

from src.dry_run import DryRunReport, PlannedChange


def _make_report(**kwargs) -> DryRunReport:
    defaults = {"pr_number": 42, "repo": "org/repo"}
    defaults.update(kwargs)
    return DryRunReport(**defaults)


class TestPlannedChange:
    def test_to_dict_contains_expected_keys(self):
        c = PlannedChange(pr_number=1, repo="a/b", action="add", label="bug", reason="matched")
        d = c.to_dict()
        assert d["pr_number"] == 1
        assert d["repo"] == "a/b"
        assert d["action"] == "add"
        assert d["label"] == "bug"
        assert d["reason"] == "matched"

    def test_reason_defaults_to_empty_string(self):
        c = PlannedChange(pr_number=1, repo="a/b", action="skip", label="wip")
        assert c.reason == ""


class TestDryRunReport:
    def test_initial_changes_empty(self):
        report = _make_report()
        assert report.changes == []

    def test_has_changes_false_when_empty(self):
        assert not _make_report().has_changes()

    def test_record_adds_change(self):
        report = _make_report()
        report.record("add", "feature", "path rule")
        assert len(report.changes) == 1
        assert report.has_changes()

    def test_record_multiple_changes(self):
        report = _make_report()
        report.record("add", "feature")
        report.record("remove", "wip")
        assert len(report.changes) == 2

    def test_to_dict_structure(self):
        report = _make_report()
        report.record("add", "docs", "docs/ path")
        d = report.to_dict()
        assert d["pr_number"] == 42
        assert d["repo"] == "org/repo"
        assert len(d["changes"]) == 1

    def test_format_summary_no_changes(self):
        report = _make_report()
        summary = report.format_summary()
        assert "no label changes" in summary
        assert "42" in summary

    def test_format_summary_with_changes(self):
        report = _make_report()
        report.record("add", "feature", "src/ matched")
        summary = report.format_summary()
        assert "ADD" in summary
        assert "feature" in summary
        assert "src/ matched" in summary

    def test_format_summary_skip_no_reason(self):
        report = _make_report()
        report.record("skip", "wip")
        summary = report.format_summary()
        assert "SKIP" in summary
        assert "wip" in summary
