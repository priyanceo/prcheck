"""Tests for src/labeler.py and src/config.py."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.labeler import LabelRule, Labeler, SizeRule


# ---------------------------------------------------------------------------
# LabelRule
# ---------------------------------------------------------------------------

class TestLabelRule:
    def test_matches_exact_pattern(self):
        rule = LabelRule(label="docs", patterns=["docs/**"])
        assert rule.matches("docs/index.md")

    def test_no_match(self):
        rule = LabelRule(label="ci", patterns=[".github/**"])
        assert not rule.matches("src/main.py")

    def test_multiple_patterns_first_matches(self):
        rule = LabelRule(label="docs", patterns=["*.md", "docs/**"])
        assert rule.matches("README.md")


# ---------------------------------------------------------------------------
# SizeRule
# ---------------------------------------------------------------------------

class TestSizeRule:
    def test_within_range(self):
        rule = SizeRule(label="size/S", min_lines=11, max_lines=50)
        assert rule.matches(30)

    def test_below_min(self):
        rule = SizeRule(label="size/S", min_lines=11, max_lines=50)
        assert not rule.matches(5)

    def test_above_max(self):
        rule = SizeRule(label="size/S", min_lines=11, max_lines=50)
        assert not rule.matches(51)

    def test_no_upper_bound(self):
        rule = SizeRule(label="size/L", min_lines=51)
        assert rule.matches(10_000)

    def test_boundary_inclusive(self):
        rule = SizeRule(label="size/XS", min_lines=0, max_lines=10)
        assert rule.matches(0)
        assert rule.matches(10)
        assert not rule.matches(11)


# ---------------------------------------------------------------------------
# Labeler
# ---------------------------------------------------------------------------

class TestLabeler:
    def _make_labeler(self) -> Labeler:
        return Labeler(
            path_rules=[
                LabelRule("docs", ["docs/**", "*.md"]),
                LabelRule("ci", [".github/**"]),
            ],
            size_rules=[
                SizeRule("size/XS", max_lines=10),
                SizeRule("size/S", min_lines=11, max_lines=50),
            ],
        )

    def test_labels_for_paths_single_match(self):
        labeler = self._make_labeler()
        assert labeler.labels_for_paths(["docs/guide.md"]) == ["docs"]

    def test_labels_for_paths_multiple_matches(self):
        labeler = self._make_labeler()
        labels = labeler.labels_for_paths(["docs/guide.md", ".github/workflows/ci.yml"])
        assert set(labels) == {"docs", "ci"}

    def test_labels_for_paths_no_duplicates(self):
        labeler = self._make_labeler()
        labels = labeler.labels_for_paths(["README.md", "docs/page.md"])
        assert labels.count("docs") == 1

    def test_labels_for_size(self):
        labeler = self._make_labeler()
        assert labeler.labels_for_size(5) == ["size/XS"]
        assert labeler.labels_for_size(25) == ["size/S"]

    def test_compute_labels_combined(self):
        labeler = self._make_labeler()
        labels = labeler.compute_labels(changed_files=["docs/api.md"], total_lines=8)
        assert "docs" in labels
        assert "size/XS" in labels

    def test_compute_labels_empty(self):
        labeler = self._make_labeler()
        assert labeler.compute_labels([], 200) == []
