"""Tests for src/label_regex.py"""

import pytest

from src.label_regex import LabelRegexFilter, RegexResult, RegexRule


# ---------------------------------------------------------------------------
# RegexRule
# ---------------------------------------------------------------------------

class TestRegexRule:
    def test_valid_rule_compiles(self):
        rule = RegexRule(pattern=r"^bug.*")
        assert rule.pattern == r"^bug.*"

    def test_blank_pattern_raises(self):
        with pytest.raises(ValueError):
            RegexRule(pattern="   ")

    def test_empty_pattern_raises(self):
        with pytest.raises(ValueError):
            RegexRule(pattern="")

    def test_matches_full_match(self):
        rule = RegexRule(pattern=r"^feature(/.*)?$")
        assert rule.matches("feature") is True
        assert rule.matches("feature/auth") is True

    def test_no_match_partial(self):
        rule = RegexRule(pattern=r"^bug$")
        assert rule.matches("bug-fix") is False

    def test_invalid_regex_raises(self):
        with pytest.raises(re.error if False else Exception):
            # re.compile raises re.error for bad patterns
            RegexRule(pattern="[invalid")


import re  # noqa: E402 – needed for the test above


# ---------------------------------------------------------------------------
# RegexResult
# ---------------------------------------------------------------------------

class TestRegexResult:
    def test_to_dict_contains_expected_keys(self):
        result = RegexResult(label="bug", allowed=True, matched_pattern=r"^bug$")
        d = result.to_dict()
        assert set(d.keys()) == {"label", "allowed", "matched_pattern"}

    def test_to_dict_values(self):
        result = RegexResult(label="chore", allowed=False, matched_pattern=None)
        d = result.to_dict()
        assert d["label"] == "chore"
        assert d["allowed"] is False
        assert d["matched_pattern"] is None


# ---------------------------------------------------------------------------
# LabelRegexFilter
# ---------------------------------------------------------------------------

def _make_filter(*patterns: str) -> LabelRegexFilter:
    return LabelRegexFilter(rules=[RegexRule(pattern=p) for p in patterns])


class TestLabelRegexFilterCheck:
    def test_no_rules_allows_everything(self):
        f = LabelRegexFilter(rules=[])
        assert f.check("anything").allowed is True
        assert f.check("anything").matched_pattern is None

    def test_matching_pattern_allows_label(self):
        f = _make_filter(r"^bug$", r"^feature$")
        result = f.check("bug")
        assert result.allowed is True
        assert result.matched_pattern == r"^bug$"

    def test_non_matching_pattern_blocks_label(self):
        f = _make_filter(r"^bug$")
        result = f.check("chore")
        assert result.allowed is False
        assert result.matched_pattern is None

    def test_first_matching_pattern_returned(self):
        f = _make_filter(r".*", r"^bug$")
        result = f.check("bug")
        assert result.matched_pattern == r".*"


class TestLabelRegexFilterFilterLabels:
    def test_returns_only_allowed(self):
        f = _make_filter(r"^(bug|feature)$")
        result = f.filter_labels(["bug", "chore", "feature", "wip"])
        assert result == ["bug", "feature"]

    def test_empty_list_returns_empty(self):
        f = _make_filter(r"^bug$")
        assert f.filter_labels([]) == []

    def test_no_rules_returns_all(self):
        f = LabelRegexFilter(rules=[])
        labels = ["a", "b", "c"]
        assert f.filter_labels(labels) == labels
