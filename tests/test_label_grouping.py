"""Tests for src/label_grouping.py."""
import pytest

from src.label_grouping import (
    GroupingResult,
    GroupingRule,
    LabelGroupingResolver,
)


# ---------------------------------------------------------------------------
# GroupingRule
# ---------------------------------------------------------------------------

class TestGroupingRule:
    def test_valid_rule(self):
        rule = GroupingRule(group="ci", members=frozenset(["ci/build", "ci/test"]))
        assert rule.group == "ci"
        assert "ci/build" in rule.members

    def test_blank_group_raises(self):
        with pytest.raises(ValueError, match="group name"):
            GroupingRule(group="   ", members=frozenset(["x"]))

    def test_empty_members_raises(self):
        with pytest.raises(ValueError, match="members"):
            GroupingRule(group="ci", members=frozenset())

    def test_members_normalised_to_lowercase(self):
        rule = GroupingRule(group="ci", members=frozenset(["CI/Build"]))
        assert "ci/build" in rule.members

    def test_members_whitespace_stripped(self):
        rule = GroupingRule(group="ci", members=frozenset(["  ci/build  "]))
        assert "ci/build" in rule.members

    def test_contains_case_insensitive(self):
        rule = GroupingRule(group="ci", members=frozenset(["ci/build"]))
        assert rule.contains("CI/Build")

    def test_contains_returns_false_for_non_member(self):
        rule = GroupingRule(group="ci", members=frozenset(["ci/build"]))
        assert not rule.contains("docs")

    def test_to_dict_keys(self):
        rule = GroupingRule(group="ci", members=frozenset(["ci/build"]))
        d = rule.to_dict()
        assert "group" in d and "members" in d


# ---------------------------------------------------------------------------
# GroupingResult
# ---------------------------------------------------------------------------

class TestGroupingResult:
    def test_to_dict_contains_expected_keys(self):
        r = GroupingResult(label="ci/build", group="ci", matched=True)
        d = r.to_dict()
        assert set(d.keys()) == {"label", "group", "matched"}

    def test_to_dict_values(self):
        r = GroupingResult(label="ci/build", group="ci", matched=True)
        assert r.to_dict()["matched"] is True
        assert r.to_dict()["group"] == "ci"


# ---------------------------------------------------------------------------
# LabelGroupingResolver
# ---------------------------------------------------------------------------

def _make_resolver() -> LabelGroupingResolver:
    resolver = LabelGroupingResolver()
    resolver.add_rule(GroupingRule(group="ci", members=frozenset(["ci/build", "ci/test"])))
    resolver.add_rule(GroupingRule(group="docs", members=frozenset(["documentation", "readme"])))
    return resolver


class TestLabelGroupingResolver:
    def test_resolve_matched(self):
        r = _make_resolver().resolve("ci/build")
        assert r.matched is True
        assert r.group == "ci"

    def test_resolve_unmatched(self):
        r = _make_resolver().resolve("unknown")
        assert r.matched is False
        assert r.group is None

    def test_resolve_case_insensitive(self):
        r = _make_resolver().resolve("CI/BUILD")
        assert r.matched is True

    def test_groups_for_labels_clusters_correctly(self):
        mapping = _make_resolver().groups_for_labels(["ci/build", "readme", "unknown"])
        assert "ci" in mapping
        assert "ci/build" in mapping["ci"]
        assert "docs" in mapping
        assert "readme" in mapping["docs"]
        assert "unknown" not in str(mapping)

    def test_groups_for_labels_empty_list(self):
        assert _make_resolver().groups_for_labels([]) == {}
