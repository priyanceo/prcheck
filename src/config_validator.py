"""Validate the raw config dict loaded from YAML before use."""
from typing import Any


class ConfigValidationError(Exception):
    """Raised when the configuration file contains invalid values."""


def _validate_path_rule(rule: Any, index: int) -> None:
    if not isinstance(rule, dict):
        raise ConfigValidationError(
            f"path_rules[{index}] must be a mapping, got {type(rule).__name__}"
        )
    if "label" not in rule:
        raise ConfigValidationError(f"path_rules[{index}] is missing required key 'label'")
    if not isinstance(rule["label"], str) or not rule["label"].strip():
        raise ConfigValidationError(f"path_rules[{index}]['label'] must be a non-empty string")
    if "patterns" not in rule:
        raise ConfigValidationError(f"path_rules[{index}] is missing required key 'patterns'")
    if not isinstance(rule["patterns"], list) or not rule["patterns"]:
        raise ConfigValidationError(
            f"path_rules[{index}]['patterns'] must be a non-empty list"
        )
    for j, pat in enumerate(rule["patterns"]):
        if not isinstance(pat, str):
            raise ConfigValidationError(
                f"path_rules[{index}]['patterns'][{j}] must be a string"
            )


def _validate_size_rule(rule: Any, index: int) -> None:
    if not isinstance(rule, dict):
        raise ConfigValidationError(
            f"size_rules[{index}] must be a mapping, got {type(rule).__name__}"
        )
    if "label" not in rule:
        raise ConfigValidationError(f"size_rules[{index}] is missing required key 'label'")
    if not isinstance(rule["label"], str) or not rule["label"].strip():
        raise ConfigValidationError(f"size_rules[{index}]['label'] must be a non-empty string")
    for key in ("min", "max"):
        if key in rule and not isinstance(rule[key], int):
            raise ConfigValidationError(
                f"size_rules[{index}]['{key}'] must be an integer"
            )
    if "min" not in rule and "max" not in rule:
        raise ConfigValidationError(
            f"size_rules[{index}] must have at least one of 'min' or 'max'"
        )
    mn = rule.get("min")
    mx = rule.get("max")
    if mn is not None and mx is not None and mn > mx:
        raise ConfigValidationError(
            f"size_rules[{index}]: 'min' ({mn}) must not exceed 'max' ({mx})"
        )


def _validate_label_filter(section: Any) -> None:
    if not isinstance(section, dict):
        raise ConfigValidationError("'label_filter' must be a mapping")
    for key in ("allow", "deny", "protected"):
        if key in section and not isinstance(section[key], list):
            raise ConfigValidationError(f"'label_filter.{key}' must be a list")
        if key in section:
            for i, item in enumerate(section[key]):
                if not isinstance(item, str):
                    raise ConfigValidationError(
                        f"'label_filter.{key}[{i}]' must be a string"
                    )


def validate_config(config: Any) -> None:
    """Raise ConfigValidationError if *config* is not a valid prcheck config."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Config must be a YAML mapping at the top level")

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

    if "label_filter" in config:
        _validate_label_filter(config["label_filter"])
