"""Tests for label_deprecation and deprecation_config."""
from __future__ import annotations

import pytest

from src.label_deprecation import DeprecationRule, DeprecationResult, LabelDeprecationChecker
from src.deprecation_config import parse_deprecation_config


# ---------------------------------------------------------------------------
# DeprecationRule
# ---------------------------------------------------------------------------

class TestDeprecationRule:
    def test_valid_rule(self):
        rule = DeprecationRule(label="old", reason="use new", replacement="new")
        assert rule.label == "old"
        assert rule.replacement == "new"

    def test_blank_label_raises(self):
        with pytest.raises(ValueError):
            DeprecationRule(label="   ")

    def test_empty_label_raises(self):
        with pytest.raises(ValueError):
            DeprecationRule(label="")

    def test_whitespace_stripped_from_label(self):
        rule = DeprecationRule(label="  old  ")
        assert rule.label == "old"

    def test_blank_replacement_becomes_none(self):
        rule = DeprecationRule(label="old", replacement="   ")
        assert rule.replacement is None

    def test_to_dict_keys(self):
        rule = DeprecationRule(label="old", reason="r", replacement="new")
        d = rule.to_dict()
        assert set(d.keys()) == {"label", "reason", "replacement"}


# ---------------------------------------------------------------------------
# LabelDeprecationChecker
# ---------------------------------------------------------------------------

class TestLabelDeprecationChecker:
    def _make_checker(self) -> LabelDeprecationChecker:
        checker = LabelDeprecationChecker()
        checker.add_rule(DeprecationRule(label="old", reason="use new", replacement="new"))
        checker.add_rule(DeprecationRule(label="legacy", reason="retired"))
        return checker

    def test_check_deprecated_label(self):
        checker = self._make_checker()
        result = checker.check("old")
        assert result.deprecated is True
        assert result.replacement == "new"

    def test_check_non_deprecated_label(self):
        checker = self._make_checker()
        result = checker.check("active")
        assert result.deprecated is False

    def test_check_case_insensitive(self):
        checker = self._make_checker()
        result = checker.check("OLD")
        assert result.deprecated is True

    def test_check_strips_whitespace(self):
        checker = self._make_checker()
        result = checker.check("  legacy  ")
        assert result.deprecated is True

    def test_check_all_returns_list(self):
        checker = self._make_checker()
        results = checker.check_all(["old", "active"])
        assert len(results) == 2
        assert results[0].deprecated is True
        assert results[1].deprecated is False

    def test_deprecated_labels_list(self):
        checker = self._make_checker()
        assert set(checker.deprecated_labels()) == {"old", "legacy"}

    def test_result_to_dict_keys(self):
        checker = self._make_checker()
        d = checker.check("old").to_dict()
        assert set(d.keys()) == {"label", "deprecated", "reason", "replacement"}


# ---------------------------------------------------------------------------
# parse_deprecation_config
# ---------------------------------------------------------------------------

class TestParseDeprecationConfigDefaults:
    def test_empty_config_returns_empty_checker(self):
        checker = parse_deprecation_config({})
        assert checker.deprecated_labels() == []

    def test_missing_deprecation_key_returns_defaults(self):
        checker = parse_deprecation_config({"other": {}})
        assert checker.deprecated_labels() == []

    def test_non_dict_section_returns_defaults(self):
        checker = parse_deprecation_config({"deprecation": "bad"})
        assert checker.deprecated_labels() == []

    def test_non_list_labels_returns_defaults(self):
        checker = parse_deprecation_config({"deprecation": {"labels": "bad"}})
        assert checker.deprecated_labels() == []


class TestParseDeprecationConfigValues:
    def _config(self):
        return {
            "deprecation": {
                "labels": [
                    {"label": "old", "reason": "use new", "replacement": "new"},
                    {"label": "legacy"},
                ]
            }
        }

    def test_parses_two_rules(self):
        checker = parse_deprecation_config(self._config())
        assert set(checker.deprecated_labels()) == {"old", "legacy"}

    def test_replacement_parsed(self):
        checker = parse_deprecation_config(self._config())
        result = checker.check("old")
        assert result.replacement == "new"

    def test_missing_replacement_defaults_to_none(self):
        checker = parse_deprecation_config(self._config())
        result = checker.check("legacy")
        assert result.replacement is None

    def test_non_dict_entry_skipped(self):
        config = {"deprecation": {"labels": ["not-a-dict", {"label": "old"}]}}
        checker = parse_deprecation_config(config)
        assert checker.deprecated_labels() == ["old"]

    def test_blank_label_entry_skipped(self):
        config = {"deprecation": {"labels": [{"label": "  "}]}}
        checker = parse_deprecation_config(config)
        assert checker.deprecated_labels() == []
