"""Tests for src/label_formatter.py."""
import pytest

from src.label_formatter import (
    FormattedLabel,
    deduplicate,
    format_label,
    format_labels,
    normalize,
)


class TestNormalize:
    def test_strips_leading_trailing_whitespace(self):
        assert normalize("  bug  ") == "bug"

    def test_lowercases(self):
        assert normalize("BugFix") == "bugfix"

    def test_replaces_spaces_with_hyphens(self):
        assert normalize("good first issue") == "good-first-issue"

    def test_replaces_underscores_with_hyphens(self):
        assert normalize("needs_review") == "needs-review"

    def test_replaces_mixed_whitespace_and_underscores(self):
        assert normalize("size_ large") == "size-large"

    def test_removes_invalid_characters(self):
        assert normalize("feat!ure") == "feature"

    def test_strips_leading_trailing_hyphens(self):
        assert normalize("!bug!") == "bug"

    def test_allows_colon(self):
        assert normalize("type:bug") == "type:bug"

    def test_allows_slash(self):
        assert normalize("area/backend") == "area/backend"

    def test_empty_string_returns_empty(self):
        assert normalize("") == ""

    def test_raises_for_non_string(self):
        with pytest.raises(TypeError, match="str"):
            normalize(123)  # type: ignore[arg-type]


class TestFormatLabel:
    def test_returns_formatted_label_instance(self):
        result = format_label("  My Label  ")
        assert isinstance(result, FormattedLabel)

    def test_raw_preserved(self):
        result = format_label("  My Label  ")
        assert result.raw == "  My Label  "

    def test_normalized_applied(self):
        result = format_label("  My Label  ")
        assert result.normalized == "my-label"

    def test_frozen_dataclass(self):
        result = format_label("bug")
        with pytest.raises((AttributeError, TypeError)):
            result.normalized = "other"  # type: ignore[misc]


class TestFormatLabels:
    def test_returns_list_of_formatted_labels(self):
        results = format_labels(["Bug", "enhancement"])
        assert len(results) == 2
        assert all(isinstance(r, FormattedLabel) for r in results)

    def test_empty_list(self):
        assert format_labels([]) == []


class TestDeduplicate:
    def test_removes_exact_duplicates(self):
        assert deduplicate(["bug", "bug"]) == ["bug"]

    def test_removes_case_insensitive_duplicates(self):
        assert deduplicate(["Bug", "bug"]) == ["Bug"]

    def test_preserves_order(self):
        assert deduplicate(["enhancement", "bug", "enhancement"]) == [
            "enhancement",
            "bug",
        ]

    def test_no_duplicates_unchanged(self):
        labels = ["bug", "enhancement", "docs"]
        assert deduplicate(labels) == labels

    def test_empty_list(self):
        assert deduplicate([]) == []
