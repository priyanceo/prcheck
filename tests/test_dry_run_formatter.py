"""Tests for src/dry_run_formatter.py"""
import os
import pytest

from src.dry_run import DryRunReport
from src.dry_run_formatter import render_dry_run_markdown, write_dry_run_summary


def _make_report(pr_number: int = 7, repo: str = "acme/prcheck") -> DryRunReport:
    return DryRunReport(pr_number=pr_number, repo=repo)


class TestRenderDryRunMarkdown:
    def test_contains_pr_number(self):
        md = render_dry_run_markdown(_make_report())
        assert "PR #7" in md

    def test_contains_repo(self):
        md = render_dry_run_markdown(_make_report())
        assert "acme/prcheck" in md

    def test_no_changes_message(self):
        md = render_dry_run_markdown(_make_report())
        assert "No label changes" in md

    def test_table_present_when_changes_exist(self):
        report = _make_report()
        report.record("add", "bug", "issue pattern")
        md = render_dry_run_markdown(report)
        assert "| Action |" in md
        assert "bug" in md

    def test_reason_in_table(self):
        report = _make_report()
        report.record("remove", "wip", "size threshold")
        md = render_dry_run_markdown(report)
        assert "size threshold" in md

    def test_empty_reason_shows_dash(self):
        report = _make_report()
        report.record("skip", "docs")
        md = render_dry_run_markdown(report)
        assert "\u2014" in md

    def test_multiple_rows(self):
        report = _make_report()
        report.record("add", "feature")
        report.record("add", "backend")
        md = render_dry_run_markdown(report)
        assert md.count("`feature`") == 1
        assert md.count("`backend`") == 1


class TestWriteDryRunSummary:
    def test_writes_to_summary_file(self, tmp_path):
        summary_file = tmp_path / "summary.md"
        report = _make_report()
        report.record("add", "ci")
        os.environ["GITHUB_STEP_SUMMARY"] = str(summary_file)
        try:
            write_dry_run_summary(report)
            content = summary_file.read_text(encoding="utf-8")
            assert "ci" in content
        finally:
            del os.environ["GITHUB_STEP_SUMMARY"]

    def test_no_error_when_env_not_set(self):
        os.environ.pop("GITHUB_STEP_SUMMARY", None)
        report = _make_report()
        write_dry_run_summary(report)  # should not raise
