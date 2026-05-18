"""Tests for label cascade resolution and config parsing."""
import pytest

from src.label_cascade import CascadeRule, CascadeResult, LabelCascadeResolver
from src.cascade_config import parse_cascade_config


# ---------------------------------------------------------------------------
# CascadeRule
# ---------------------------------------------------------------------------

class TestCascadeRule:
    def test_valid_rule(self):
        rule = CascadeRule(trigger="backend", cascades=["python", "needs-review"])
        assert rule.trigger == "backend"
        assert rule.cascades == ["python", "needs-review"]

    def test_trigger_normalised_to_lowercase(self):
        rule = CascadeRule(trigger="  Backend  ", cascades=["python"])
        assert rule.trigger == "backend"

    def test_cascades_normalised_to_lowercase(self):
        rule = CascadeRule(trigger="backend", cascades=["Python", "Needs-Review"])
        assert rule.cascades == ["python", "needs-review"]

    def test_blank_trigger_raises(self):
        with pytest.raises(ValueError, match="trigger"):
            CascadeRule(trigger="  ", cascades=["python"])

    def test_empty_cascades_raises(self):
        with pytest.raises(ValueError, match="cascades"):
            CascadeRule(trigger="backend", cascades=[])

    def test_blank_cascade_label_raises(self):
        with pytest.raises(ValueError, match="blank"):
            CascadeRule(trigger="backend", cascades=["  "])

    def test_to_dict(self):
        rule = CascadeRule(trigger="backend", cascades=["python"])
        d = rule.to_dict()
        assert d["trigger"] == "backend"
        assert d["cascades"] == ["python"]


# ---------------------------------------------------------------------------
# LabelCascadeResolver
# ---------------------------------------------------------------------------

def _make_resolver(*rules: CascadeRule) -> LabelCascadeResolver:
    return LabelCascadeResolver(list(rules))


class TestLabelCascadeResolver:
    def test_no_results_when_trigger_absent(self):
        rule = CascadeRule(trigger="backend", cascades=["python"])
        resolver = _make_resolver(rule)
        results = resolver.resolve({"frontend"})
        assert results == []

    def test_applied_when_trigger_present(self):
        rule = CascadeRule(trigger="backend", cascades=["python"])
        resolver = _make_resolver(rule)
        results = resolver.resolve({"backend"})
        assert len(results) == 1
        assert results[0].applied == ["python"]
        assert results[0].skipped == []

    def test_skipped_when_cascade_already_active(self):
        rule = CascadeRule(trigger="backend", cascades=["python"])
        resolver = _make_resolver(rule)
        results = resolver.resolve({"backend", "python"})
        assert results[0].skipped == ["python"]
        assert results[0].applied == []

    def test_all_cascaded_returns_only_new_labels(self):
        rule = CascadeRule(trigger="backend", cascades=["python", "needs-review"])
        resolver = _make_resolver(rule)
        new_labels = resolver.all_cascaded({"backend", "python"})
        assert new_labels == {"needs-review"}

    def test_all_cascaded_empty_when_no_trigger(self):
        rule = CascadeRule(trigger="backend", cascades=["python"])
        resolver = _make_resolver(rule)
        assert resolver.all_cascaded({"frontend"}) == set()


# ---------------------------------------------------------------------------
# parse_cascade_config
# ---------------------------------------------------------------------------

class TestParseCascadeConfig:
    def test_empty_config_returns_resolver(self):
        resolver = parse_cascade_config({})
        assert isinstance(resolver, LabelCascadeResolver)

    def test_missing_cascade_key_returns_empty(self):
        resolver = parse_cascade_config({"other": []})
        assert resolver.all_cascaded({"backend"}) == set()

    def test_non_list_cascade_section_returns_empty(self):
        resolver = parse_cascade_config({"cascade": "bad"})
        assert resolver.all_cascaded({"backend"}) == set()

    def test_valid_config_builds_rules(self):
        config = {
            "cascade": [
                {"trigger": "backend", "cascades": ["python", "needs-review"]}
            ]
        }
        resolver = parse_cascade_config(config)
        assert resolver.all_cascaded({"backend"}) == {"python", "needs-review"}

    def test_non_dict_entry_skipped(self):
        config = {"cascade": ["not-a-dict", {"trigger": "backend", "cascades": ["python"]}]}
        resolver = parse_cascade_config(config)
        assert resolver.all_cascaded({"backend"}) == {"python"}

    def test_entry_missing_cascades_skipped(self):
        config = {"cascade": [{"trigger": "backend"}]}
        resolver = parse_cascade_config(config)
        assert resolver.all_cascaded({"backend"}) == set()

    def test_blank_cascade_labels_filtered(self):
        config = {"cascade": [{"trigger": "backend", "cascades": ["  ", "python"]}]}
        resolver = parse_cascade_config(config)
        assert resolver.all_cascaded({"backend"}) == {"python"}
