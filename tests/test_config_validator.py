"""Tests for src/config_validator.py."""

import pytest

from src.config_validator import ConfigValidationError, validate_config


VALID_CONFIG = {
    "path_rules": [
        {"label": "docs", "patterns": ["docs/**", "*.md"]},
        {"label": "backend", "patterns": ["src/**"]},
    ],
    "size_rules": [
        {"label": "small", "max": 50},
        {"label": "medium", "min": 51, "max": 200},
        {"label": "large", "min": 201},
    ],
}


class TestValidateConfigRoot:
    def test_valid_config_passes(self):
        validate_config(VALID_CONFIG)  # should not raise

    def test_empty_config_passes(self):
        validate_config({})  # no rules defined is acceptable

    def test_non_dict_raises(self):
        with pytest.raises(ConfigValidationError, match="root must be a mapping"):
            validate_config(["path_rules"])

    def test_path_rules_not_list_raises(self):
        with pytest.raises(ConfigValidationError, match="'path_rules' must be a list"):
            validate_config({"path_rules": "docs/**"})

    def test_size_rules_not_list_raises(self):
        with pytest.raises(ConfigValidationError, match="'size_rules' must be a list"):
            validate_config({"size_rules": {"label": "large", "min": 100}})


class TestValidatePathRule:
    def test_missing_label_raises(self):
        with pytest.raises(ConfigValidationError, match="missing required field 'label'"):
            validate_config({"path_rules": [{"patterns": ["src/**"]}]})

    def test_empty_label_raises(self):
        with pytest.raises(ConfigValidationError, match="non-empty string"):
            validate_config({"path_rules": [{"label": "", "patterns": ["src/**"]}]})

    def test_missing_patterns_raises(self):
        with pytest.raises(ConfigValidationError, match="missing required field 'patterns'"):
            validate_config({"path_rules": [{"label": "docs"}]})

    def test_empty_patterns_list_raises(self):
        with pytest.raises(ConfigValidationError, match="non-empty list"):
            validate_config({"path_rules": [{"label": "docs", "patterns": []}]})

    def test_non_string_pattern_raises(self):
        with pytest.raises(ConfigValidationError, match="non-empty string"):
            validate_config({"path_rules": [{"label": "docs", "patterns": [123]}]})

    def test_rule_not_dict_raises(self):
        with pytest.raises(ConfigValidationError, match="must be a mapping"):
            validate_config({"path_rules": ["docs/**"]})


class TestValidateSizeRule:
    def test_missing_label_raises(self):
        with pytest.raises(ConfigValidationError, match="missing required field 'label'"):
            validate_config({"size_rules": [{"max": 100}]})

    def test_no_min_or_max_raises(self):
        with pytest.raises(ConfigValidationError, match="at least one of 'min' or 'max'"):
            validate_config({"size_rules": [{"label": "large"}]})

    def test_negative_min_raises(self):
        with pytest.raises(ConfigValidationError, match="non-negative integer"):
            validate_config({"size_rules": [{"label": "x", "min": -1}]})

    def test_min_greater_than_max_raises(self):
        with pytest.raises(ConfigValidationError, match="must not exceed 'max'"):
            validate_config({"size_rules": [{"label": "x", "min": 200, "max": 100}]})

    def test_only_min_is_valid(self):
        validate_config({"size_rules": [{"label": "large", "min": 500}]})

    def test_only_max_is_valid(self):
        validate_config({"size_rules": [{"label": "small", "max": 50}]})

    def test_rule_not_dict_raises(self):
        with pytest.raises(ConfigValidationError, match="must be a mapping"):
            validate_config({"size_rules": ["large"]})
