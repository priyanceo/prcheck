"""Tests for src/label_filter.py."""
import pytest
from src.label_filter import (
    LabelFilter,
    LabelFilterConfig,
    FilterResult,
    parse_label_filter_config,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_filter(
    allow_list=None,
    deny_list=None,
    protected_labels=None,
) -> LabelFilter:
    return LabelFilter(
        LabelFilterConfig(
            allow_list=allow_list or [],
            deny_list=deny_list or [],
            protected_labels=protected_labels or [],
        )
    )


# ---------------------------------------------------------------------------
# FilterResult
# ---------------------------------------------------------------------------

class TestFilterResult:
    def test_to_dict_contains_expected_keys(self):
        result = FilterResult(label="bug", allowed=True, reason="ok")
        d = result.to_dict()
        assert set(d.keys()) == {"label", "allowed", "reason"}

    def test_to_dict_values(self):
        result = FilterResult(label="wip", allowed=False, reason="in deny_list")
        assert result.to_dict()["label"] == "wip"
        assert result.to_dict()["allowed"] is False


# ---------------------------------------------------------------------------
# check_add
# ---------------------------------------------------------------------------

class TestCheckAdd:
    def test_no_restrictions_allows_any_label(self):
        f = _make_filter()
        assert f.check_add("bug").allowed is True

    def test_allow_list_blocks_unlisted_label(self):
        f = _make_filter(allow_list=["feature", "bug"])
        result = f.check_add("wip")
        assert result.allowed is False
        assert result.reason == "not in allow_list"

    def test_allow_list_permits_listed_label(self):
        f = _make_filter(allow_list=["feature"])
        assert f.check_add("feature").allowed is True

    def test_deny_list_blocks_listed_label(self):
        f = _make_filter(deny_list=["wip"])
        result = f.check_add("wip")
        assert result.allowed is False
        assert result.reason == "in deny_list"

    def test_deny_list_does_not_block_other_labels(self):
        f = _make_filter(deny_list=["wip"])
        assert f.check_add("bug").allowed is True


# ---------------------------------------------------------------------------
# check_remove
# ---------------------------------------------------------------------------

class TestCheckRemove:
    def test_unprotected_label_can_be_removed(self):
        f = _make_filter()
        assert f.check_remove("bug").allowed is True

    def test_protected_label_cannot_be_removed(self):
        f = _make_filter(protected_labels=["do-not-touch"])
        result = f.check_remove("do-not-touch")
        assert result.allowed is False
        assert result.reason == "protected"


# ---------------------------------------------------------------------------
# filter_additions / filter_removals
# ---------------------------------------------------------------------------

class TestFilterHelpers:
    def test_filter_additions_removes_denied(self):
        f = _make_filter(deny_list=["wip"])
        assert f.filter_additions(["bug", "wip", "feature"]) == ["bug", "feature"]

    def test_filter_removals_keeps_unprotected(self):
        f = _make_filter(protected_labels=["keep"])
        assert f.filter_removals(["bug", "keep"]) == ["bug"]


# ---------------------------------------------------------------------------
# parse_label_filter_config
# ---------------------------------------------------------------------------

class TestParseLabelFilterConfig:
    def test_empty_config_returns_defaults(self):
        cfg = parse_label_filter_config({})
        assert cfg.allow_list == []
        assert cfg.deny_list == []
        assert cfg.protected_labels == []

    def test_parses_allow_deny_protected(self):
        raw = {
            "label_filter": {
                "allow": ["bug", "feature"],
                "deny": ["wip"],
                "protected": ["critical"],
            }
        }
        cfg = parse_label_filter_config(raw)
        assert cfg.allow_list == ["bug", "feature"]
        assert cfg.deny_list == ["wip"]
        assert cfg.protected_labels == ["critical"]

    def test_missing_label_filter_key_returns_defaults(self):
        cfg = parse_label_filter_config({"other_key": {}})
        assert cfg.allow_list == []
