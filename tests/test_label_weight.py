"""Tests for label_weight and weight_config."""
import pytest

from src.label_weight import LabelWeightResolver, WeightRule
from src.weight_config import parse_weight_config


# ---------------------------------------------------------------------------
# WeightRule
# ---------------------------------------------------------------------------

class TestWeightRule:
    def test_valid_rule(self):
        rule = WeightRule(label="bug", weight=2.5)
        assert rule.label == "bug"
        assert rule.weight == 2.5

    def test_default_weight_is_one(self):
        rule = WeightRule(label="bug")
        assert rule.weight == 1.0

    def test_blank_label_raises(self):
        with pytest.raises(ValueError, match="blank"):
            WeightRule(label="   ")

    def test_negative_weight_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            WeightRule(label="bug", weight=-1.0)

    def test_zero_weight_is_valid(self):
        rule = WeightRule(label="wontfix", weight=0.0)
        assert rule.weight == 0.0

    def test_to_dict(self):
        rule = WeightRule(label="bug", weight=3.0)
        d = rule.to_dict()
        assert d["label"] == "bug"
        assert d["weight"] == 3.0


# ---------------------------------------------------------------------------
# LabelWeightResolver
# ---------------------------------------------------------------------------

class TestLabelWeightResolver:
    def _make_resolver(self) -> LabelWeightResolver:
        resolver = LabelWeightResolver(default_weight=1.0)
        resolver.add_rule(WeightRule(label="bug", weight=5.0))
        resolver.add_rule(WeightRule(label="docs", weight=0.5))
        return resolver

    def test_resolve_known_label(self):
        resolver = self._make_resolver()
        result = resolver.resolve("bug")
        assert result.weight == 5.0
        assert "bug" in result.reason

    def test_resolve_case_insensitive(self):
        resolver = self._make_resolver()
        result = resolver.resolve("BUG")
        assert result.weight == 5.0

    def test_resolve_unknown_label_uses_default(self):
        resolver = self._make_resolver()
        result = resolver.resolve("unknown")
        assert result.weight == 1.0
        assert "default" in result.reason

    def test_rank_sorts_descending(self):
        resolver = self._make_resolver()
        ranked = resolver.rank(["docs", "bug", "unknown"])
        assert ranked[0].label == "bug"
        assert ranked[1].label == "unknown"
        assert ranked[2].label == "docs"

    def test_rank_empty_list(self):
        resolver = self._make_resolver()
        assert resolver.rank([]) == []

    def test_to_dict_on_result(self):
        resolver = self._make_resolver()
        d = resolver.resolve("bug").to_dict()
        assert set(d.keys()) == {"label", "weight", "reason"}


# ---------------------------------------------------------------------------
# parse_weight_config
# ---------------------------------------------------------------------------

class TestParseWeightConfigDefaults:
    def test_empty_config_returns_defaults(self):
        resolver = parse_weight_config({})
        assert resolver.default_weight == 1.0

    def test_missing_weights_key_returns_defaults(self):
        resolver = parse_weight_config({"other": True})
        assert resolver.default_weight == 1.0

    def test_non_dict_weights_section_returns_defaults(self):
        resolver = parse_weight_config({"weights": "bad"})
        assert resolver.default_weight == 1.0


class TestParseWeightConfigValues:
    def test_custom_default_weight(self):
        resolver = parse_weight_config({"weights": {"default": 2.0}})
        assert resolver.default_weight == 2.0

    def test_label_rules_loaded(self):
        config = {
            "weights": {
                "labels": [
                    {"label": "bug", "weight": 4.0},
                    {"label": "docs", "weight": 0.25},
                ]
            }
        }
        resolver = parse_weight_config(config)
        assert resolver.resolve("bug").weight == 4.0
        assert resolver.resolve("docs").weight == 0.25

    def test_invalid_entry_skipped(self):
        config = {
            "weights": {
                "labels": [
                    {"label": "", "weight": 1.0},
                    {"label": "bug", "weight": -1},
                    "not-a-dict",
                    {"label": "valid", "weight": 3.0},
                ]
            }
        }
        resolver = parse_weight_config(config)
        assert resolver.resolve("valid").weight == 3.0
        assert resolver.resolve("bug").weight == resolver.default_weight
