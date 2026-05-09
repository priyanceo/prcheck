"""Tests for src/expiry_config.py."""

import pytest

from src.expiry_config import LabelExpiryConfig, parse_expiry_config


class TestParseExpiryConfigDefaults:
    def test_empty_config_returns_empty_ttls(self):
        cfg = parse_expiry_config({})
        assert cfg.ttl_by_label == {}

    def test_missing_expiry_key_returns_defaults(self):
        cfg = parse_expiry_config({"path_rules": []})
        assert isinstance(cfg, LabelExpiryConfig)

    def test_non_dict_expiry_section_returns_defaults(self):
        cfg = parse_expiry_config({"expiry": "bad"})
        assert cfg.ttl_by_label == {}

    def test_non_list_labels_returns_defaults(self):
        cfg = parse_expiry_config({"expiry": {"labels": "bad"}})
        assert cfg.ttl_by_label == {}


class TestParseExpiryConfigValues:
    def test_ttl_seconds_parsed(self):
        cfg = parse_expiry_config({"expiry": {"labels": [{"label": "stale", "ttl_seconds": 60}]}})
        assert cfg.ttl_by_label["stale"] == 60.0

    def test_ttl_hours_converted(self):
        cfg = parse_expiry_config({"expiry": {"labels": [{"label": "needs-review", "ttl_hours": 2}]}})
        assert cfg.ttl_by_label["needs-review"] == 7200.0

    def test_ttl_days_converted(self):
        cfg = parse_expiry_config({"expiry": {"labels": [{"label": "old", "ttl_days": 1}]}})
        assert cfg.ttl_by_label["old"] == 86400.0

    def test_multiple_labels_parsed(self):
        cfg = parse_expiry_config({
            "expiry": {
                "labels": [
                    {"label": "stale", "ttl_days": 7},
                    {"label": "bug", "ttl_hours": 48},
                ]
            }
        })
        assert len(cfg.ttl_by_label) == 2
        assert cfg.ttl_by_label["stale"] == 7 * 86400

    def test_zero_ttl_entry_excluded(self):
        cfg = parse_expiry_config({"expiry": {"labels": [{"label": "stale", "ttl_seconds": 0}]}})
        assert "stale" not in cfg.ttl_by_label

    def test_entry_without_label_skipped(self):
        cfg = parse_expiry_config({"expiry": {"labels": [{"ttl_days": 1}]}})
        assert cfg.ttl_by_label == {}

    def test_ttl_for_known_label(self):
        cfg = parse_expiry_config({"expiry": {"labels": [{"label": "stale", "ttl_seconds": 30}]}})
        assert cfg.ttl_for("stale") == 30.0

    def test_ttl_for_unknown_label_returns_none(self):
        cfg = parse_expiry_config({})
        assert cfg.ttl_for("ghost") is None
