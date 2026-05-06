"""Tests for PRSummary."""

import pytest
from src.pr_summary import PRSummary


def _make_summary(**kwargs) -> PRSummary:
    defaults = {"pr_number": 42, "repo": "org/repo"}
    defaults.update(kwargs)
    return PRSummary(**defaults)


class TestPRSummaryMutations:
    def test_add_label_appends(self):
        s = _make_summary()
        s.add_label("bug")
        assert "bug" in s.labels_added

    def test_add_label_no_duplicates(self):
        s = _make_summary()
        s.add_label("bug")
        s.add_label("bug")
        assert s.labels_added.count("bug") == 1

    def test_remove_label_appends(self):
        s = _make_summary()
        s.remove_label("wip")
        assert "wip" in s.labels_removed

    def test_skip_label_appends(self):
        s = _make_summary()
        s.skip_label("enhancement")
        assert "enhancement" in s.labels_skipped

    def test_add_matched_rule_no_duplicates(self):
        s = _make_summary()
        s.add_matched_rule("docs-rule")
        s.add_matched_rule("docs-rule")
        assert s.matched_rules.count("docs-rule") == 1


class TestPRSummaryToDict:
    def test_to_dict_keys(self):
        s = _make_summary(total_changes=10)
        d = s.to_dict()
        assert set(d.keys()) == {
            "pr_number", "repo", "labels_added",
            "labels_removed", "labels_skipped",
            "total_changes", "matched_rules",
        }

    def test_to_dict_values(self):
        s = _make_summary(total_changes=5)
        s.add_label("size-s")
        d = s.to_dict()
        assert d["pr_number"] == 42
        assert d["total_changes"] == 5
        assert d["labels_added"] == ["size-s"]


class TestPRSummaryFormatSummary:
    def test_contains_pr_number(self):
        s = _make_summary()
        assert "#42" in s.format_summary()

    def test_shows_no_changes_when_empty(self):
        s = _make_summary()
        assert "No label changes" in s.format_summary()

    def test_shows_added_labels(self):
        s = _make_summary()
        s.add_label("backend")
        out = s.format_summary()
        assert "backend" in out
        assert "Added" in out

    def test_shows_total_changes(self):
        s = _make_summary(total_changes=200)
        assert "200" in s.format_summary()
