"""Validates the structure and values of prcheck configuration."""

from typing import Any


class ConfigValidationError(Exception):
    """Raised when configuration is invalid."""
    pass


def _validate_path_rule(rule: Any, index: int) -> None:
    """Validate a single path-based label rule entry."""
    if not isinstance(rule, dict):
        raise ConfigValidationError(
            f"path_rules[{index}] must be a mapping, got {type(rule).__name__}"
        )
    if "label" not in rule:
        raise ConfigValidationError(
            f"path_rules[{index}] is missing required field 'label'"
        )
    if not isinstance(rule["label"], str) or not rule["label"].strip():
        raise ConfigValidationError(
            f"path_rules[{index}]['label'] must be a non-empty string"
        )
    if "patterns" not in rule:
        raise ConfigValidationError(
            f"path_rules[{index}] is missing required field 'patterns'"
        )
    if not isinstance(rule["patterns"], list) or len(rule["patterns"]) == 0:
        raise ConfigValidationError(
            f"path_rules[{index}]['patterns'] must be a non-empty list"
        )
    for i, pattern in enumerate(rule["patterns"]):
        if not isinstance(pattern, str) or not pattern.strip():
            raise ConfigValidationError(
                f"path_rules[{index}]['patterns'][{i}] must be a non-empty string"
            )


def _validate_size_rule(rule: Any, index: int) -> None:
    """Validate a single size-based label rule entry."""
    if not isinstance(rule, dict):
        raise ConfigValidationError(
            f"size_rules[{index}] must be a mapping, got {type(rule).__name__}"
        )
    if "label" not in rule:
        raise ConfigValidationError(
            f"size_rules[{index}] is missing required field 'label'"
        )
    if not isinstance(rule["label"], str) or not rule["label"].strip():
        raise ConfigValidationError(
            f"size_rules[{index}]['label'] must be a non-empty string"
        )
    if "min" not in rule and "max" not in rule:
        raise ConfigValidationError(
            f"size_rules[{index}] must have at least one of 'min' or 'max'"
        )
    for field in ("min", "max"):
        if field in rule:
            if not isinstance(rule[field], int) or rule[field] < 0:
                raise ConfigValidationError(
                    f"size_rules[{index}]['{field}'] must be a non-negative integer"
                )
    if "min" in rule and "max" in rule and rule["min"] > rule["max"]:
        raise ConfigValidationError(
            f"size_rules[{index}]: 'min' ({rule['min']}) must not exceed 'max' ({rule['max']})"
        )


def validate_config(config: Any) -> None:
    """Validate the full configuration dictionary.

    Raises ConfigValidationError if any part of the config is invalid.
    """
    if not isinstance(config, dict):
        raise ConfigValidationError(
            f"Configuration root must be a mapping, got {type(config).__name__}"
        )

    path_rules = config.get("path_rules", [])
    if not isinstance(path_rules, list):
        raise ConfigValidationError("'path_rules' must be a list")
    for i, rule in enumerate(path_rules):
        _validate_path_rule(rule, i)

    size_rules = config.get("size_rules", [])
    if not isinstance(size_rules, list):
        raise ConfigValidationError("'size_rules' must be a list")
    for i, rule in enumerate(size_rules):
        _validate_size_rule(rule, i)
