"""Tests for label inheritance module and config parser."""
from __future__ import annotations

import pytest

from src.label_inheritance import (
    InheritanceRule,
    InheritanceResult,
    LabelInheritanceResolver,
)
from src.inheritance_config import parse_inheritance_config


# ---------------------------------------------------------------------------
# InheritanceRule
# ---------------------------------------------------------------------------

class TestInheritanceRule:
    def test_valid_rule(self):
        rule = InheritanceRule(label="feature", inherits_from=["needs-review"])
        assert rule.label == "feature"
        assert rule.inherits_from == ["needs-review"]

    def test_blank_label_raises(self):
        with pytest.raises(ValueError, match="label"):
            InheritanceRule(label="  ", inherits_from=["parent"])

    def test_empty_inherits_from_raises(self):
        with pytest.raises(ValueError, match="inherits_from"):
            InheritanceRule(label="child", inherits_from=[])

    def test_blank_parent_raises(self):
        with pytest.raises(ValueError, match="blank"):
            InheritanceRule(label="child", inherits_from=["valid", ""])

    def test_whitespace_stripped_from_label(self):
        rule = InheritanceRule(label="  bug  ", inherits_from=["triage"])
        assert rule.label == "bug"

    def test_to_dict(self):
        rule = InheritanceRule(label="feat", inherits_from=["p1", "p2"])
        d = rule.to_dict()
        assert d["label"] == "feat"
        assert d["inherits_from"] == ["p1", "p2"]


# ---------------------------------------------------------------------------
# InheritanceResult
# ---------------------------------------------------------------------------

class TestInheritanceResult:
    def test_to_dict_keys(self):
        r = InheritanceResult(label="x", added_parents=["a"], already_present=["b"])
        d = r.to_dict()
        assert set(d.keys()) == {"label", "added_parents", "already_present"}

    def test_to_dict_values(self):
        r = InheritanceResult(label="x", added_parents=["a"], already_present=[])
        assert r.to_dict()["added_parents"] == ["a"]


# ---------------------------------------------------------------------------
# LabelInheritanceResolver
# ---------------------------------------------------------------------------

def _make_resolver():
    rules = [
        InheritanceRule(label="feature", inherits_from=["needs-review", "triage"]),
        InheritanceRule(label="hotfix", inherits_from=["urgent"]),
    ]
    return LabelInheritanceResolver(rules)


class TestLabelInheritanceResolver:
    def test_resolve_adds_missing_parents(self):
        resolver = _make_resolver()
        result = resolver.resolve("feature", current_labels=set())
        assert sorted(result.added_parents) == ["needs-review", "triage"]
        assert result.already_present == []

    def test_resolve_skips_present_parents(self):
        resolver = _make_resolver()
        result = resolver.resolve("feature", current_labels={"needs-review"})
        assert result.added_parents == ["triage"]
        assert result.already_present == ["needs-review"]

    def test_resolve_unknown_label_returns_empty(self):
        resolver = _make_resolver()
        result = resolver.resolve("unknown", current_labels=set())
        assert result.added_parents == []

    def test_resolve_all_covers_all_labels(self):
        resolver = _make_resolver()
        results = resolver.resolve_all({"feature", "hotfix"})
        assert "feature" in results
        assert "hotfix" in results


# ---------------------------------------------------------------------------
# parse_inheritance_config
# ---------------------------------------------------------------------------

class TestParseInheritanceConfig:
    def test_empty_config_returns_resolver(self):
        resolver = parse_inheritance_config({})
        assert isinstance(resolver, LabelInheritanceResolver)

    def test_missing_section_returns_empty_resolver(self):
        resolver = parse_inheritance_config({"other": []})
        result = resolver.resolve("any", set())
        assert result.added_parents == []

    def test_non_list_section_returns_empty_resolver(self):
        resolver = parse_inheritance_config({"inheritance": "bad"})
        result = resolver.resolve("any", set())
        assert result.added_parents == []

    def test_valid_section_parsed(self):
        cfg = {
            "inheritance": [
                {"label": "feature", "inherits_from": ["triage"]}
            ]
        }
        resolver = parse_inheritance_config(cfg)
        result = resolver.resolve("feature", set())
        assert result.added_parents == ["triage"]

    def test_malformed_entry_skipped(self):
        cfg = {
            "inheritance": [
                "not-a-dict",
                {"label": "ok", "inherits_from": ["parent"]},
            ]
        }
        resolver = parse_inheritance_config(cfg)
        result = resolver.resolve("ok", set())
        assert result.added_parents == ["parent"]

    def test_invalid_rule_skipped_silently(self):
        cfg = {
            "inheritance": [
                {"label": "", "inherits_from": ["parent"]},
            ]
        }
        resolver = parse_inheritance_config(cfg)
        assert isinstance(resolver, LabelInheritanceResolver)
