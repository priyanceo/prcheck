"""Tests for src/label_exclusion.py."""
from __future__ import annotations

import pytest

from src.label_exclusion import (
    ExclusionResult,
    ExclusionRule,
    LabelExclusionEnforcer,
)


# ---------------------------------------------------------------------------
# ExclusionRule
# ---------------------------------------------------------------------------

class TestExclusionRule:
    def test_valid_rule(self):
        rule = ExclusionRule(label="bug", excluded_when=frozenset({"wontfix"}))
        assert rule.label == "bug"

    def test_blank_label_raises(self):
        with pytest.raises(ValueError, match="blank"):
            ExclusionRule(label="  ", excluded_when=frozenset({"wontfix"}))

    def test_empty_label_raises(self):
        with pytest.raises(ValueError, match="blank"):
            ExclusionRule(label="", excluded_when=frozenset({"wontfix"}))

    def test_empty_excluded_when_raises(self):
        with pytest.raises(ValueError, match="excluded_when"):
            ExclusionRule(label="bug", excluded_when=frozenset())

    def test_is_excluded_true_when_trigger_present(self):
        rule = ExclusionRule(label="bug", excluded_when=frozenset({"wontfix", "duplicate"}))
        assert rule.is_excluded({"wontfix"}) is True

    def test_is_excluded_false_when_no_trigger_present(self):
        rule = ExclusionRule(label="bug", excluded_when=frozenset({"wontfix"}))
        assert rule.is_excluded({"enhancement"}) is False

    def test_is_excluded_false_for_empty_present(self):
        rule = ExclusionRule(label="bug", excluded_when=frozenset({"wontfix"}))
        assert rule.is_excluded(set()) is False


# ---------------------------------------------------------------------------
# ExclusionResult
# ---------------------------------------------------------------------------

class TestExclusionResult:
    def test_to_dict_contains_expected_keys(self):
        result = ExclusionResult(label="bug", allowed=False, blocked_by=["wontfix"])
        d = result.to_dict()
        assert set(d.keys()) == {"label", "allowed", "blocked_by"}

    def test_to_dict_values(self):
        result = ExclusionResult(label="bug", allowed=False, blocked_by=["wontfix"])
        d = result.to_dict()
        assert d["label"] == "bug"
        assert d["allowed"] is False
        assert d["blocked_by"] == ["wontfix"]

    def test_allowed_result_has_empty_blocked_by(self):
        result = ExclusionResult(label="feature", allowed=True)
        assert result.to_dict()["blocked_by"] == []


# ---------------------------------------------------------------------------
# LabelExclusionEnforcer
# ---------------------------------------------------------------------------

def _make_enforcer() -> LabelExclusionEnforcer:
    rules = [
        ExclusionRule(label="bug", excluded_when=frozenset({"wontfix", "duplicate"})),
        ExclusionRule(label="urgent", excluded_when=frozenset({"on-hold"})),
    ]
    return LabelExclusionEnforcer(rules)


class TestLabelExclusionEnforcer:
    def test_allowed_when_no_rule_exists(self):
        enforcer = _make_enforcer()
        result = enforcer.check("unknown-label", {"wontfix"})
        assert result.allowed is True

    def test_blocked_when_trigger_present(self):
        enforcer = _make_enforcer()
        result = enforcer.check("bug", {"duplicate"})
        assert result.allowed is False
        assert "duplicate" in result.blocked_by

    def test_allowed_when_trigger_absent(self):
        enforcer = _make_enforcer()
        result = enforcer.check("bug", {"enhancement"})
        assert result.allowed is True
        assert result.blocked_by == []

    def test_blocked_by_is_sorted(self):
        enforcer = _make_enforcer()
        result = enforcer.check("bug", {"wontfix", "duplicate"})
        assert result.blocked_by == sorted(result.blocked_by)

    def test_filter_labels_removes_excluded(self):
        enforcer = _make_enforcer()
        allowed = enforcer.filter_labels(["bug", "urgent", "docs"], {"wontfix"})
        assert "bug" not in allowed
        assert "urgent" in allowed
        assert "docs" in allowed

    def test_filter_labels_empty_candidates(self):
        enforcer = _make_enforcer()
        assert enforcer.filter_labels([], {"wontfix"}) == []

    def test_filter_labels_no_present_labels(self):
        enforcer = _make_enforcer()
        result = enforcer.filter_labels(["bug", "urgent"], set())
        assert result == ["bug", "urgent"]
