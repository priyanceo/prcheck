"""Tests for parse_lifecycle_config."""
import pytest

from src.lifecycle_config import LifecycleConfig, parse_lifecycle_config


class TestParseLifecycleConfigDefaults:
    def test_empty_config_returns_defaults(self):
        cfg = parse_lifecycle_config({})
        assert cfg.track_created is True
        assert cfg.track_updated is True
        assert cfg.track_removed is True
        assert cfg.report_enabled is True
        assert cfg.tracked_labels == []

    def test_missing_lifecycle_key_returns_defaults(self):
        cfg = parse_lifecycle_config({"other": {}})
        assert cfg.track_created is True

    def test_non_dict_config_returns_defaults(self):
        cfg = parse_lifecycle_config("bad")
        assert cfg.track_created is True

    def test_non_dict_lifecycle_section_returns_defaults(self):
        cfg = parse_lifecycle_config({"lifecycle": "bad"})
        assert cfg.report_enabled is True


class TestParseLifecycleConfigValues:
    def test_track_created_false(self):
        cfg = parse_lifecycle_config({"lifecycle": {"track_created": False}})
        assert cfg.track_created is False

    def test_track_removed_false(self):
        cfg = parse_lifecycle_config({"lifecycle": {"track_removed": False}})
        assert cfg.track_removed is False

    def test_report_enabled_false(self):
        cfg = parse_lifecycle_config({"lifecycle": {"report_enabled": False}})
        assert cfg.report_enabled is False

    def test_tracked_labels_parsed(self):
        cfg = parse_lifecycle_config({"lifecycle": {"tracked_labels": ["bug", "feat"]}})
        assert cfg.tracked_labels == ["bug", "feat"]

    def test_non_list_tracked_labels_ignored(self):
        cfg = parse_lifecycle_config({"lifecycle": {"tracked_labels": "bug"}})
        assert cfg.tracked_labels == []

    def test_blank_tracked_labels_stripped(self):
        cfg = parse_lifecycle_config({"lifecycle": {"tracked_labels": ["  ", "bug"]}})
        assert cfg.tracked_labels == ["bug"]


class TestLifecycleConfigShouldTrack:
    def test_tracks_all_by_default(self):
        cfg = LifecycleConfig()
        assert cfg.should_track("bug", "created") is True
        assert cfg.should_track("bug", "updated") is True
        assert cfg.should_track("bug", "removed") is True

    def test_does_not_track_disabled_event(self):
        cfg = LifecycleConfig(track_removed=False)
        assert cfg.should_track("bug", "removed") is False

    def test_does_not_track_unlisted_label(self):
        cfg = LifecycleConfig(tracked_labels=["feat"])
        assert cfg.should_track("bug", "created") is False

    def test_tracks_listed_label(self):
        cfg = LifecycleConfig(tracked_labels=["bug"])
        assert cfg.should_track("bug", "created") is True

    def test_unknown_event_returns_false(self):
        cfg = LifecycleConfig()
        assert cfg.should_track("bug", "reopened") is False
