"""Tests for src/cooldown_config.py"""
from __future__ import annotations

import pytest

from src.cooldown_config import parse_cooldown_config
from src.label_cooldown import CooldownConfig


class TestParseCooldownConfigDefaults:
    def test_empty_config_returns_defaults(self):
        cfg = parse_cooldown_config({})
        assert isinstance(cfg, CooldownConfig)
        assert cfg.default_seconds == 0
        assert cfg.per_label == {}

    def test_missing_cooldown_key_returns_defaults(self):
        cfg = parse_cooldown_config({"other": True})
        assert cfg.default_seconds == 0

    def test_non_dict_cooldown_section_returns_defaults(self):
        cfg = parse_cooldown_config({"cooldown": "bad"})
        assert cfg.default_seconds == 0

    def test_null_cooldown_section_returns_defaults(self):
        cfg = parse_cooldown_config({"cooldown": None})
        assert cfg.default_seconds == 0


class TestParseCooldownConfigValues:
    def test_default_seconds_parsed(self):
        cfg = parse_cooldown_config({"cooldown": {"default_seconds": 1800}})
        assert cfg.default_seconds == 1800

    def test_invalid_default_seconds_falls_back(self):
        cfg = parse_cooldown_config({"cooldown": {"default_seconds": -10}})
        assert cfg.default_seconds == 0

    def test_non_int_default_seconds_falls_back(self):
        cfg = parse_cooldown_config({"cooldown": {"default_seconds": "fast"}})
        assert cfg.default_seconds == 0

    def test_per_label_entries_parsed(self):
        raw = {
            "cooldown": {
                "labels": [
                    {"label": "bug", "seconds": 3600},
                    {"label": "wip", "seconds": 900},
                ]
            }
        }
        cfg = parse_cooldown_config(raw)
        assert cfg.per_label["bug"] == 3600
        assert cfg.per_label["wip"] == 900

    def test_non_dict_label_entry_skipped(self):
        raw = {"cooldown": {"labels": ["not-a-dict"]}}
        cfg = parse_cooldown_config(raw)
        assert cfg.per_label == {}

    def test_blank_label_skipped(self):
        raw = {"cooldown": {"labels": [{"label": "  ", "seconds": 60}]}}
        cfg = parse_cooldown_config(raw)
        assert cfg.per_label == {}

    def test_negative_seconds_skipped(self):
        raw = {"cooldown": {"labels": [{"label": "bug", "seconds": -1}]}}
        cfg = parse_cooldown_config(raw)
        assert cfg.per_label == {}

    def test_label_key_normalised_to_lowercase(self):
        raw = {"cooldown": {"labels": [{"label": "Bug", "seconds": 60}]}}
        cfg = parse_cooldown_config(raw)
        assert "bug" in cfg.per_label
