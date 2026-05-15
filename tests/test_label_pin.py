"""Tests for src/label_pin.py."""
import pytest

from src.label_pin import LabelPinEnforcer, PinConfig, PinResult, parse_pin_config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_enforcer(*pinned: str) -> LabelPinEnforcer:
    return LabelPinEnforcer(PinConfig(pinned=frozenset(p.lower() for p in pinned)))


# ---------------------------------------------------------------------------
# PinConfig
# ---------------------------------------------------------------------------

class TestPinConfig:
    def test_is_pinned_returns_true_for_pinned_label(self):
        cfg = PinConfig(pinned=frozenset(["do-not-remove"]))
        assert cfg.is_pinned("do-not-remove") is True

    def test_is_pinned_case_insensitive(self):
        cfg = PinConfig(pinned=frozenset(["wip"]))
        assert cfg.is_pinned("WIP") is True

    def test_is_pinned_strips_whitespace(self):
        cfg = PinConfig(pinned=frozenset(["wip"]))
        assert cfg.is_pinned("  wip  ") is True

    def test_is_pinned_returns_false_for_unknown(self):
        cfg = PinConfig(pinned=frozenset(["wip"]))
        assert cfg.is_pinned("bug") is False

    def test_empty_config_never_pinned(self):
        cfg = PinConfig()
        assert cfg.is_pinned("anything") is False


# ---------------------------------------------------------------------------
# PinResult
# ---------------------------------------------------------------------------

class TestPinResult:
    def test_to_dict_contains_expected_keys(self):
        r = PinResult(blocked=["wip"], allowed=["bug"])
        d = r.to_dict()
        assert "blocked" in d and "allowed" in d

    def test_to_dict_values(self):
        r = PinResult(blocked=["wip"], allowed=["bug"])
        assert r.to_dict() == {"blocked": ["wip"], "allowed": ["bug"]}


# ---------------------------------------------------------------------------
# LabelPinEnforcer
# ---------------------------------------------------------------------------

class TestLabelPinEnforcer:
    def test_pinned_label_is_blocked(self):
        enforcer = _make_enforcer("wip")
        result = enforcer.check_removals(["wip", "bug"])
        assert "wip" in result.blocked
        assert "bug" in result.allowed

    def test_no_pinned_labels_all_allowed(self):
        enforcer = _make_enforcer()
        result = enforcer.check_removals(["bug", "feature"])
        assert result.blocked == []
        assert set(result.allowed) == {"bug", "feature"}

    def test_filter_removals_excludes_pinned(self):
        enforcer = _make_enforcer("do-not-remove")
        allowed = enforcer.filter_removals(["do-not-remove", "chore"])
        assert allowed == ["chore"]

    def test_filter_removals_empty_input(self):
        enforcer = _make_enforcer("wip")
        assert enforcer.filter_removals([]) == []


# ---------------------------------------------------------------------------
# parse_pin_config
# ---------------------------------------------------------------------------

class TestParsePinConfig:
    def test_empty_config_returns_empty_pinset(self):
        assert parse_pin_config({}).pinned == frozenset()

    def test_missing_pin_key_returns_defaults(self):
        assert parse_pin_config({"other": {}}).pinned == frozenset()

    def test_non_dict_pin_section_returns_defaults(self):
        assert parse_pin_config({"pin": "bad"}).pinned == frozenset()

    def test_non_list_labels_returns_defaults(self):
        assert parse_pin_config({"pin": {"labels": "wip"}}).pinned == frozenset()

    def test_valid_labels_parsed(self):
        cfg = parse_pin_config({"pin": {"labels": ["WIP", "do-not-remove"]}})
        assert cfg.pinned == frozenset(["wip", "do-not-remove"])

    def test_blank_entries_skipped(self):
        cfg = parse_pin_config({"pin": {"labels": ["", "  ", "wip"]}})
        assert cfg.pinned == frozenset(["wip"])

    def test_non_string_entries_skipped(self):
        cfg = parse_pin_config({"pin": {"labels": [42, None, "wip"]}})
        assert cfg.pinned == frozenset(["wip"])
