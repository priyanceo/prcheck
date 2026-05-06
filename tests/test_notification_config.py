"""Tests for src/notification_config.py."""
from __future__ import annotations

import pytest

from src.notification_config import NotificationConfig, parse_notification_config


class TestParseNotificationConfigDefaults:
    def test_empty_config_returns_defaults(self):
        cfg = parse_notification_config({})
        assert cfg.enabled is True
        assert cfg.output_path is None
        assert cfg.log_level == "INFO"

    def test_missing_notifications_key_returns_defaults(self):
        cfg = parse_notification_config({"path_rules": []})
        assert cfg.enabled is True


class TestParseNotificationConfigValues:
    def test_enabled_false(self):
        cfg = parse_notification_config({"notifications": {"enabled": False}})
        assert cfg.enabled is False

    def test_output_path_set(self):
        cfg = parse_notification_config(
            {"notifications": {"output_path": "/tmp/out.jsonl"}}
        )
        assert cfg.output_path == "/tmp/out.jsonl"

    def test_log_level_debug(self):
        cfg = parse_notification_config({"notifications": {"log_level": "DEBUG"}})
        assert cfg.log_level == "DEBUG"

    def test_all_fields_set(self):
        cfg = parse_notification_config(
            {
                "notifications": {
                    "enabled": True,
                    "output_path": "/var/log/prcheck.jsonl",
                    "log_level": "WARNING",
                }
            }
        )
        assert cfg.enabled is True
        assert cfg.output_path == "/var/log/prcheck.jsonl"
        assert cfg.log_level == "WARNING"


class TestParseNotificationConfigValidation:
    def test_notifications_not_dict_raises(self):
        with pytest.raises(ValueError, match="must be a mapping"):
            parse_notification_config({"notifications": "yes"})

    def test_enabled_non_bool_raises(self):
        with pytest.raises(ValueError, match="must be a boolean"):
            parse_notification_config({"notifications": {"enabled": "yes"}})

    def test_output_path_non_string_raises(self):
        with pytest.raises(ValueError, match="must be a string"):
            parse_notification_config({"notifications": {"output_path": 123}})

    def test_invalid_log_level_raises(self):
        with pytest.raises(ValueError, match="log_level"):
            parse_notification_config({"notifications": {"log_level": "VERBOSE"}})
