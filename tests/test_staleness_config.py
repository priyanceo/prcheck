"""Tests for src/staleness_config.py."""
import pytest

from src.staleness_config import StalenessConfig, parse_staleness_config


class TestParseStalenessConfigDefaults:
    def test_empty_config_returns_defaults(self):
        cfg = parse_staleness_config({})
        assert cfg.enabled is True
        assert cfg.default_stale_after_days == 30
        assert cfg.per_label_days == {}

    def test_missing_staleness_key_returns_defaults(self):
        cfg = parse_staleness_config({"other": "value"})
        assert cfg.default_stale_after_days == 30

    def test_non_dict_staleness_section_returns_defaults(self):
        cfg = parse_staleness_config({"staleness": "yes"})
        assert cfg.enabled is True


class TestParseStalenessConfigValues:
    def test_enabled_false(self):
        cfg = parse_staleness_config({"staleness": {"enabled": False}})
        assert cfg.enabled is False

    def test_custom_default_days(self):
        cfg = parse_staleness_config({"staleness": {"stale_after_days": 14}})
        assert cfg.default_stale_after_days == 14

    def test_per_label_days_parsed(self):
        cfg = parse_staleness_config(
            {"staleness": {"per_label": {"bug": 7, "wip": 60}}}
        )
        assert cfg.per_label_days == {"bug": 7, "wip": 60}

    def test_invalid_per_label_entry_skipped(self):
        cfg = parse_staleness_config(
            {"staleness": {"per_label": {"bug": -1, "wip": "lots"}}}
        )
        assert cfg.per_label_days == {}

    def test_non_dict_per_label_ignored(self):
        cfg = parse_staleness_config({"staleness": {"per_label": ["bug"]}})
        assert cfg.per_label_days == {}


class TestStalenessConfigStaledays:
    def test_returns_per_label_override(self):
        cfg = StalenessConfig(default_stale_after_days=30, per_label_days={"wip": 5})
        assert cfg.stale_days_for("wip") == 5

    def test_falls_back_to_default(self):
        cfg = StalenessConfig(default_stale_after_days=30, per_label_days={})
        assert cfg.stale_days_for("unknown") == 30
