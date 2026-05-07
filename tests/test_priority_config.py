"""Tests for parse_priority_config."""
import pytest

from src.label_priority import LabelPriorityResolver
from src.priority_config import parse_priority_config


class TestParsePriorityConfigDefaults:
    def test_empty_config_returns_resolver(self):
        resolver = parse_priority_config({})
        assert isinstance(resolver, LabelPriorityResolver)

    def test_missing_section_no_cap(self):
        resolver = parse_priority_config({})
        result = resolver.resolve(["a", "b", "c"])
        assert result.dropped == []

    def test_empty_section_no_cap(self):
        resolver = parse_priority_config({"label_priority": {}})
        result = resolver.resolve(["x"])
        assert result.ordered == ["x"]


class TestParsePriorityConfigValues:
    def test_max_labels_respected(self):
        config = {"label_priority": {"max_labels": 1, "rules": []}}
        resolver = parse_priority_config(config)
        result = resolver.resolve(["a", "b"])
        assert len(result.ordered) == 1
        assert len(result.dropped) == 1

    def test_rules_set_priority_order(self):
        config = {
            "label_priority": {
                "rules": [
                    {"label": "hotfix", "priority": 99},
                    {"label": "docs", "priority": 1},
                ]
            }
        }
        resolver = parse_priority_config(config)
        result = resolver.resolve(["docs", "hotfix"])
        assert result.ordered[0] == "hotfix"

    def test_blank_label_in_rules_skipped(self):
        config = {
            "label_priority": {
                "rules": [
                    {"label": "", "priority": 5},
                    {"label": "bug", "priority": 10},
                ]
            }
        }
        resolver = parse_priority_config(config)
        result = resolver.resolve(["bug"])
        assert result.ordered == ["bug"]

    def test_max_labels_as_string_coerced(self):
        config = {"label_priority": {"max_labels": "2", "rules": []}}
        resolver = parse_priority_config(config)
        result = resolver.resolve(["a", "b", "c"])
        assert len(result.ordered) == 2
