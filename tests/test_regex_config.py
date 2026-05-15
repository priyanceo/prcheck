"""Tests for src/regex_config.py"""

import pytest

from src.regex_config import parse_regex_config


class TestParseRegexConfigDefaults:
    def test_empty_config_returns_allow_all(self):
        f = parse_regex_config({})
        assert f.check("anything").allowed is True

    def test_missing_section_returns_allow_all(self):
        f = parse_regex_config({"other": {}})
        assert f.check("bug").allowed is True

    def test_non_dict_section_returns_allow_all(self):
        f = parse_regex_config({"label_regex": "bad"})
        assert f.check("bug").allowed is True

    def test_missing_patterns_key_returns_allow_all(self):
        f = parse_regex_config({"label_regex": {}})
        assert f.check("bug").allowed is True

    def test_non_list_patterns_returns_allow_all(self):
        f = parse_regex_config({"label_regex": {"patterns": "not-a-list"}})
        assert f.check("bug").allowed is True


class TestParseRegexConfigValues:
    def _cfg(self, *patterns):
        return {"label_regex": {"patterns": list(patterns)}}

    def test_single_pattern_allows_match(self):
        f = parse_regex_config(self._cfg(r"^bug$"))
        assert f.check("bug").allowed is True

    def test_single_pattern_blocks_non_match(self):
        f = parse_regex_config(self._cfg(r"^bug$"))
        assert f.check("chore").allowed is False

    def test_multiple_patterns(self):
        f = parse_regex_config(self._cfg(r"^bug$", r"^feature$"))
        assert f.check("feature").allowed is True
        assert f.check("wip").allowed is False

    def test_blank_entries_skipped(self):
        f = parse_regex_config(self._cfg("", "   ", r"^bug$"))
        assert f.check("bug").allowed is True
        assert f.check("other").allowed is False

    def test_non_string_entries_skipped(self):
        f = parse_regex_config({"label_regex": {"patterns": [123, None, r"^ok$"]}})
        assert f.check("ok").allowed is True

    def test_invalid_regex_entry_skipped(self):
        # "[invalid" is a bad regex; it should be skipped, leaving no rules → allow-all
        f = parse_regex_config(self._cfg("[invalid"))
        assert f.check("anything").allowed is True

    def test_whitespace_stripped_from_pattern(self):
        f = parse_regex_config(self._cfg("  ^bug$  "))
        assert f.check("bug").allowed is True
