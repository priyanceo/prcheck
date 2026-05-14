"""Tests for src/alias_config.py."""
from __future__ import annotations

from src.alias_config import parse_alias_config


class TestParseAliasConfigDefaults:
    def test_empty_config_returns_empty_map(self):
        result = parse_alias_config({})
        assert len(result) == 0

    def test_missing_aliases_key_returns_empty_map(self):
        result = parse_alias_config({"other": "value"})
        assert len(result) == 0

    def test_non_list_aliases_returns_empty_map(self):
        result = parse_alias_config({"aliases": "not-a-list"})
        assert len(result) == 0

    def test_non_dict_entry_skipped(self):
        result = parse_alias_config({"aliases": ["bad-entry"]})
        assert len(result) == 0


class TestParseAliasConfigValues:
    def test_single_alias_parsed(self):
        cfg = {"aliases": [{"alias": "bug", "canonical": "bug-report"}]}
        result = parse_alias_config(cfg)
        assert result.resolve("bug") == "bug-report"

    def test_multiple_aliases_parsed(self):
        cfg = {
            "aliases": [
                {"alias": "feat", "canonical": "feature"},
                {"alias": "fix", "canonical": "bug-report"},
            ]
        }
        result = parse_alias_config(cfg)
        assert result.resolve("feat") == "feature"
        assert result.resolve("fix") == "bug-report"
        assert len(result) == 2

    def test_entry_missing_alias_key_skipped(self):
        cfg = {"aliases": [{"canonical": "feature"}]}
        result = parse_alias_config(cfg)
        assert len(result) == 0

    def test_entry_missing_canonical_key_skipped(self):
        cfg = {"aliases": [{"alias": "feat"}]}
        result = parse_alias_config(cfg)
        assert len(result) == 0

    def test_blank_alias_skipped_gracefully(self):
        cfg = {"aliases": [{"alias": "", "canonical": "feature"}]}
        result = parse_alias_config(cfg)
        assert len(result) == 0

    def test_non_string_values_skipped(self):
        cfg = {"aliases": [{"alias": 123, "canonical": "feature"}]}
        result = parse_alias_config(cfg)
        assert len(result) == 0
