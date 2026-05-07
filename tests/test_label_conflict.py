"""Tests for src/label_conflict.py"""
import pytest
from src.label_conflict import (
    ConflictRule,
    ConflictResult,
    LabelConflictResolver,
    parse_conflict_rules,
)


def _make_resolver(*groups: tuple) -> LabelConflictResolver:
    """Helper: build a resolver from (group_name, [labels]) tuples."""
    rules = [ConflictRule(group=g, labels=list(ls)) for g, ls in groups]
    return LabelConflictResolver(rules)


class TestConflictRule:
    def test_conflicts_when_both_labels_in_group(self):
        rule = ConflictRule(group="size", labels=["small", "large"])
        assert rule.conflicts_with("small", "large") is True

    def test_no_conflict_when_one_label_missing(self):
        rule = ConflictRule(group="size", labels=["small", "large"])
        assert rule.conflicts_with("small", "medium") is False

    def test_no_conflict_when_neither_in_group(self):
        rule = ConflictRule(group="size", labels=["small", "large"])
        assert rule.conflicts_with("bug", "feature") is False


class TestConflictResult:
    def test_to_dict_contains_expected_keys(self):
        result = ConflictResult(resolved=["a"], dropped={"b": "reason"})
        d = result.to_dict()
        assert "resolved" in d
        assert "dropped" in d

    def test_to_dict_values(self):
        result = ConflictResult(resolved=["x"], dropped={"y": "conflicts"})
        d = result.to_dict()
        assert d["resolved"] == ["x"]
        assert d["dropped"] == {"y": "conflicts"}


class TestLabelConflictResolverNoConflicts:
    def test_no_rules_returns_all_labels(self):
        resolver = LabelConflictResolver([])
        result = resolver.resolve(["bug", "feature", "docs"])
        assert result.resolved == ["bug", "feature", "docs"]
        assert result.dropped == {}

    def test_empty_labels_returns_empty(self):
        resolver = _make_resolver(("size", ["small", "large"]))
        result = resolver.resolve([])
        assert result.resolved == []
        assert result.dropped == {}

    def test_single_label_no_conflict(self):
        resolver = _make_resolver(("size", ["small", "large"]))
        result = resolver.resolve(["small"])
        assert result.resolved == ["small"]
        assert result.dropped == {}


class TestLabelConflictResolverWithConflicts:
    def test_second_label_in_group_is_dropped(self):
        resolver = _make_resolver(("size", ["small", "large"]))
        result = resolver.resolve(["small", "large"])
        assert result.resolved == ["small"]
        assert "large" in result.dropped

    def test_first_label_wins(self):
        resolver = _make_resolver(("size", ["small", "medium", "large"]))
        result = resolver.resolve(["large", "small", "medium"])
        assert result.resolved == ["large"]
        assert "small" in result.dropped
        assert "medium" in result.dropped

    def test_non_conflicting_labels_preserved(self):
        resolver = _make_resolver(("size", ["small", "large"]))
        result = resolver.resolve(["small", "bug", "large"])
        assert "small" in result.resolved
        assert "bug" in result.resolved
        assert "large" in result.dropped

    def test_drop_reason_mentions_winner_and_group(self):
        resolver = _make_resolver(("size", ["small", "large"]))
        result = resolver.resolve(["small", "large"])
        reason = result.dropped["large"]
        assert "small" in reason
        assert "size" in reason

    def test_multiple_groups_independent(self):
        resolver = _make_resolver(
            ("size", ["small", "large"]),
            ("priority", ["low", "high"]),
        )
        result = resolver.resolve(["small", "low", "large", "high"])
        assert "small" in result.resolved
        assert "low" in result.resolved
        assert "large" in result.dropped
        assert "high" in result.dropped


class TestParseConflictRules:
    def test_empty_config_returns_empty_list(self):
        assert parse_conflict_rules({}) == []

    def test_parses_single_group(self):
        config = {
            "label_conflicts": [
                {"group": "size", "labels": ["small", "large"]}
            ]
        }
        rules = parse_conflict_rules(config)
        assert len(rules) == 1
        assert rules[0].group == "size"
        assert rules[0].labels == ["small", "large"]

    def test_skips_entry_missing_group(self):
        config = {
            "label_conflicts": [
                {"labels": ["small", "large"]}
            ]
        }
        assert parse_conflict_rules(config) == []

    def test_skips_entry_missing_labels(self):
        config = {
            "label_conflicts": [
                {"group": "size"}
            ]
        }
        assert parse_conflict_rules(config) == []

    def test_parses_multiple_groups(self):
        config = {
            "label_conflicts": [
                {"group": "size", "labels": ["small", "large"]},
                {"group": "priority", "labels": ["low", "high"]},
            ]
        }
        rules = parse_conflict_rules(config)
        assert len(rules) == 2
