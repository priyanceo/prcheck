"""Tests for src/label_dependency.py."""

from __future__ import annotations

import pytest

from src.label_dependency import (
    DependencyResult,
    DependencyRule,
    LabelDependencyEnforcer,
)


# ---------------------------------------------------------------------------
# DependencyRule
# ---------------------------------------------------------------------------

class TestDependencyRule:
    def test_valid_rule(self):
        rule = DependencyRule(label="deploy", requires=["approved", "tested"])
        assert rule.label == "deploy"
        assert rule.requires == ["approved", "tested"]

    def test_blank_label_raises(self):
        with pytest.raises(ValueError, match="label must not be blank"):
            DependencyRule(label="  ", requires=["approved"])

    def test_empty_requires_raises(self):
        with pytest.raises(ValueError, match="requires must contain"):
            DependencyRule(label="deploy", requires=[])

    def test_missing_deps_all_present(self):
        rule = DependencyRule(label="deploy", requires=["approved", "tested"])
        assert rule.missing_deps({"approved", "tested", "other"}) == []

    def test_missing_deps_some_absent(self):
        rule = DependencyRule(label="deploy", requires=["approved", "tested"])
        missing = rule.missing_deps({"approved"})
        assert missing == ["tested"]

    def test_missing_deps_all_absent(self):
        rule = DependencyRule(label="deploy", requires=["approved", "tested"])
        missing = rule.missing_deps(set())
        assert set(missing) == {"approved", "tested"}


# ---------------------------------------------------------------------------
# DependencyResult
# ---------------------------------------------------------------------------

class TestDependencyResult:
    def test_to_dict_contains_expected_keys(self):
        result = DependencyResult(label="deploy", allowed=False, missing=["approved"])
        d = result.to_dict()
        assert set(d.keys()) == {"label", "allowed", "missing"}

    def test_to_dict_values(self):
        result = DependencyResult(label="deploy", allowed=False, missing=["approved"])
        d = result.to_dict()
        assert d["label"] == "deploy"
        assert d["allowed"] is False
        assert d["missing"] == ["approved"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_enforcer() -> LabelDependencyEnforcer:
    return LabelDependencyEnforcer([
        DependencyRule(label="deploy", requires=["approved", "tested"]),
        DependencyRule(label="release", requires=["deploy"]),
    ])


# ---------------------------------------------------------------------------
# LabelDependencyEnforcer
# ---------------------------------------------------------------------------

class TestLabelDependencyEnforcer:
    def test_no_rule_always_allowed(self):
        enforcer = _make_enforcer()
        result = enforcer.check("unknown-label", present=set())
        assert result.allowed is True
        assert result.missing == []

    def test_allowed_when_deps_satisfied(self):
        enforcer = _make_enforcer()
        result = enforcer.check("deploy", present={"approved", "tested"})
        assert result.allowed is True
        assert result.missing == []

    def test_blocked_when_dep_missing(self):
        enforcer = _make_enforcer()
        result = enforcer.check("deploy", present={"approved"})
        assert result.allowed is False
        assert "tested" in result.missing

    def test_check_all_returns_only_ruled_labels(self):
        enforcer = _make_enforcer()
        results = enforcer.check_all(
            candidates={"deploy", "release", "bug"},
            present={"approved", "tested", "deploy"},
        )
        labels = {r.label for r in results}
        assert labels == {"deploy", "release"}

    def test_check_all_correct_allowed_flags(self):
        enforcer = _make_enforcer()
        results = enforcer.check_all(
            candidates={"deploy", "release"},
            present={"approved", "tested", "deploy"},
        )
        by_label = {r.label: r for r in results}
        assert by_label["deploy"].allowed is True
        assert by_label["release"].allowed is True

    def test_check_all_empty_candidates(self):
        enforcer = _make_enforcer()
        results = enforcer.check_all(candidates=set(), present={"approved"})
        assert results == []
