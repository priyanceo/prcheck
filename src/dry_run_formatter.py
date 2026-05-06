"""Render a DryRunReport as a GitHub Step Summary markdown table."""
from __future__ import annotations

import os

from src.dry_run import DryRunReport

_ACTION_EMOJI = {
    "add": "\u2795",
    "remove": "\u2796",
    "skip": "\u23ed\ufe0f",
}


def render_dry_run_markdown(report: DryRunReport) -> str:
    """Return a markdown string summarising the dry-run report."""
    lines: list[str] = [
        f"## \U0001f9ea Dry-Run Report — PR #{report.pr_number}",
        f"**Repo:** `{report.repo}`  ",
        "",
    ]

    if not report.has_changes():
        lines.append("_No label changes would be applied._")
        return "\n".join(lines)

    lines += [
        "| Action | Label | Reason |",
        "|--------|-------|--------|",
    ]
    for c in report.changes:
        emoji = _ACTION_EMOJI.get(c.action, c.action)
        reason = c.reason or "—"
        lines.append(f"| {emoji} {c.action} | `{c.label}` | {reason} |")

    return "\n".join(lines)


def write_dry_run_summary(report: DryRunReport) -> None:
    """Write the markdown report to GITHUB_STEP_SUMMARY if available."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    markdown = render_dry_run_markdown(report)
    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write(markdown + "\n")
