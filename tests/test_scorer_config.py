"""Tests for src/scorer_config.py."""
import pytest
from src.scorer_config import parse_scorer_config


class TestParseScorerConfigDefaults:
    def test_empty_config_returns_defaults(self):
        result = parse_scorer_config({})
        assert result["threshold"] == 0.0
        assert result["default_rule_weight"] == 1.0

    def test_missing_scorer_key_returns_defaults(self):
        result = parse_scorer_config({"other": "value"})
        assert result["threshold"] == 0.0
        assert result["default_rule_weight"] == 1.0

    def test_non_dict_scorer_section_returns_defaults(self):
        result = parse_scorer_config({"scorer": "bad"})
        assert result["threshold"] == 0.0
        assert result["default_rule_weight"] == 1.0


class TestParseScorerConfigValues:
    def test_threshold_parsed(self):
        result = parse_scorer_config({"scorer": {"threshold": 0.5}})
        assert result["threshold"] == pytest.approx(0.5)

    def test_threshold_clamped_above_one(self):
        result = parse_scorer_config({"scorer": {"threshold": 5.0}})
        assert result["threshold"] == 1.0

    def test_threshold_clamped_below_zero(self):
        result = parse_scorer_config({"scorer": {"threshold": -0.5}})
        assert result["threshold"] == 0.0

    def test_default_rule_weight_parsed(self):
        result = parse_scorer_config({"scorer": {"default_rule_weight": 3.0}})
        assert result["default_rule_weight"] == pytest.approx(3.0)

    def test_non_positive_weight_falls_back_to_default(self):
        result = parse_scorer_config({"scorer": {"default_rule_weight": -1}})
        assert result["default_rule_weight"] == 1.0

    def test_invalid_threshold_type_falls_back(self):
        result = parse_scorer_config({"scorer": {"threshold": "high"}})
        assert result["threshold"] == 0.0

    def test_invalid_weight_type_falls_back(self):
        result = parse_scorer_config({"scorer": {"default_rule_weight": None}})
        assert result["default_rule_weight"] == 1.0
