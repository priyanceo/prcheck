"""Tests for src/quota_config.py."""
from src.quota_config import parse_quota_config


class TestParseQuotaConfigDefaults:
    def test_empty_config_returns_defaults(self):
        cfg = parse_quota_config({})
        assert cfg.max_labels == 10
        assert cfg.overflow_strategy == "drop"

    def test_missing_quota_key_returns_defaults(self):
        cfg = parse_quota_config({"other": "stuff"})
        assert cfg.max_labels == 10

    def test_non_dict_quota_section_returns_defaults(self):
        cfg = parse_quota_config({"quota": "invalid"})
        assert cfg.max_labels == 10
        assert cfg.overflow_strategy == "drop"

    def test_null_quota_section_returns_defaults(self):
        cfg = parse_quota_config({"quota": None})
        assert cfg.max_labels == 10


class TestParseQuotaConfigValues:
    def test_max_labels_parsed(self):
        cfg = parse_quota_config({"quota": {"max_labels": 5}})
        assert cfg.max_labels == 5

    def test_overflow_strategy_warn_parsed(self):
        cfg = parse_quota_config({"quota": {"overflow_strategy": "warn"}})
        assert cfg.overflow_strategy == "warn"

    def test_overflow_strategy_drop_parsed(self):
        cfg = parse_quota_config({"quota": {"overflow_strategy": "drop"}})
        assert cfg.overflow_strategy == "drop"

    def test_invalid_strategy_falls_back_to_default(self):
        cfg = parse_quota_config({"quota": {"overflow_strategy": "silent"}})
        assert cfg.overflow_strategy == "drop"

    def test_max_labels_zero_falls_back_to_default(self):
        cfg = parse_quota_config({"quota": {"max_labels": 0}})
        assert cfg.max_labels == 10

    def test_max_labels_negative_falls_back_to_default(self):
        cfg = parse_quota_config({"quota": {"max_labels": -3}})
        assert cfg.max_labels == 10

    def test_max_labels_non_int_falls_back_to_default(self):
        cfg = parse_quota_config({"quota": {"max_labels": "five"}})
        assert cfg.max_labels == 10
