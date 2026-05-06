"""Tests for summary_formatter.render_markdown and write_step_summary."""

import os
import pytest
from src.pr_summary import PRSummary
from src.summary_formatter import render_markdown, write_step_summary


def _make_summary(**kwargs) -> PRSummary:
    defaults = {"pr_number": 7, "repo": "acme/prcheck"}
    defaults.update(kwargs)
    return PRSummary(**defaults)


class TestRenderMarkdown:
    def test_contains_pr_number_heading(self):
        md = render_markdown(_make_summary())
        assert "## prcheck — PR #7" in md

    def test_contains_repo(self):
        md = render_markdown(_make_summary())
        assert "acme/prcheck" in md

    def test_added_labels_section_present(self):
        s = _make_summary()
        s.add_label("backend")
        md = render_markdown(s)
        assert "Labels Added" in md
        assert "backend" in md

    def test_removed_labels_section_present(self):
        s = _make_summary()
        s.remove_label("wip")
        md = render_markdown(s)
        assert "Labels Removed" in md
        assert "wip" in md

    def test_skipped_labels_section_present(self):
        s = _make_summary()
        s.skip_label("size-xl")
        md = render_markdown(s)
        assert "Skipped" in md
        assert "size-xl" in md

    def test_no_changes_message_when_empty(self):
        md = render_markdown(_make_summary())
        assert "No label changes" in md

    def test_no_changes_message_absent_when_labels_added(self):
        s = _make_summary()
        s.add_label("docs")
        md = render_markdown(s)
        assert "No label changes" not in md

    def test_matched_rules_section(self):
        s = _make_summary()
        s.add_matched_rule("path-rule-docs")
        md = render_markdown(s)
        assert "Matched Rules" in md
        assert "path-rule-docs" in md

    def test_total_changes_shown(self):
        s = _make_summary(total_changes=150)
        md = render_markdown(s)
        assert "150" in md


class TestWriteStepSummary:
    def test_creates_file(self, tmp_path):
        out = str(tmp_path / "summary.md")
        write_step_summary(_make_summary(), out)
        assert os.path.exists(out)

    def test_file_contains_markdown(self, tmp_path):
        out = str(tmp_path / "summary.md")
        s = _make_summary()
        s.add_label("ci")
        write_step_summary(s, out)
        content = open(out).read()
        assert "prcheck" in content
        assert "ci" in content
