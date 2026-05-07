"""Tests for src/throttle_config.py"""
from __future__ import annotations

from src.label_throttle import ThrottleConfig
from src.throttle_config import parse_throttle_config


class TestParseThrottleConfigDefaults:
    def test_empty_config_returns_defaults(self) -> None:
        result = parse_throttle_config({})
        assert isinstance(result, ThrottleConfig)
        assert result.window_seconds == 3600
        assert result.max_operations == 5

    def test_missing_throttle_key_returns_defaults(self) -> None:
        result = parse_throttle_config({"path_rules": []})
        assert result.window_seconds == 3600
        assert result.max_operations == 5

    def test_non_dict_throttle_section_returns_defaults(self) -> None:
        result = parse_throttle_config({"throttle": "yes"})
        assert result.window_seconds == 3600
        assert result.max_operations == 5


class TestParseThrottleConfigValues:
    def test_custom_window(self) -> None:
        result = parse_throttle_config({"throttle": {"window_seconds": 300}})
        assert result.window_seconds == 300

    def test_custom_max_operations(self) -> None:
        result = parse_throttle_config({"throttle": {"max_operations": 10}})
        assert result.max_operations == 10

    def test_both_custom_values(self) -> None:
        result = parse_throttle_config(
            {"throttle": {"window_seconds": 120, "max_operations": 2}}
        )
        assert result.window_seconds == 120
        assert result.max_operations == 2

    def test_zero_window_falls_back_to_default(self) -> None:
        result = parse_throttle_config({"throttle": {"window_seconds": 0}})
        assert result.window_seconds == 3600

    def test_negative_max_ops_falls_back_to_default(self) -> None:
        result = parse_throttle_config({"throttle": {"max_operations": -1}})
        assert result.max_operations == 5

    def test_non_int_window_falls_back_to_default(self) -> None:
        result = parse_throttle_config({"throttle": {"window_seconds": "fast"}})
        assert result.window_seconds == 3600
