"""Tests for src/label_alias.py."""
from __future__ import annotations

import pytest

from src.label_alias import AliasMap


class TestAliasMapAdd:
    def test_add_valid_alias(self):
        am = AliasMap()
        am.add("bug", "bug-report")
        assert am.all_mappings() == {"bug": "bug-report"}

    def test_blank_alias_raises(self):
        am = AliasMap()
        with pytest.raises(ValueError, match="alias"):
            am.add("", "bug-report")

    def test_blank_canonical_raises(self):
        am = AliasMap()
        with pytest.raises(ValueError, match="canonical"):
            am.add("bug", "")

    def test_whitespace_stripped(self):
        am = AliasMap()
        am.add("  bug  ", "  bug-report  ")
        assert am.resolve("bug") == "bug-report"

    def test_len_reflects_count(self):
        am = AliasMap()
        am.add("a", "alpha")
        am.add("b", "beta")
        assert len(am) == 2


class TestAliasMapResolve:
    def test_resolves_known_alias(self):
        am = AliasMap()
        am.add("feat", "feature")
        assert am.resolve("feat") == "feature"

    def test_returns_label_when_no_alias(self):
        am = AliasMap()
        assert am.resolve("unknown") == "unknown"

    def test_resolve_all_deduplicates(self):
        am = AliasMap()
        am.add("feat", "feature")
        result = am.resolve_all(["feat", "feature", "bug"])
        assert result == ["feature", "bug"]

    def test_resolve_all_preserves_order(self):
        am = AliasMap()
        am.add("b", "beta")
        result = am.resolve_all(["alpha", "b", "gamma"])
        assert result == ["alpha", "beta", "gamma"]

    def test_resolve_all_empty_list(self):
        am = AliasMap()
        assert am.resolve_all([]) == []


class TestAliasMapAliasesFor:
    def test_returns_aliases_for_canonical(self):
        am = AliasMap()
        am.add("bug", "bug-report")
        am.add("defect", "bug-report")
        aliases = am.aliases_for("bug-report")
        assert sorted(aliases) == ["bug", "defect"]

    def test_returns_empty_when_no_aliases(self):
        am = AliasMap()
        assert am.aliases_for("nonexistent") == []
