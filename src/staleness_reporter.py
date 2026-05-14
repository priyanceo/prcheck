"""Render and write staleness reports as Markdown step summaries."""
from __future__ import annotations

import os
from typing import Optional

from src.label_staleness import StalenessReport


def render_staleness_markdown(report: StalenessReport) -> str:
    lines = [
        f"## 🕒 Label Staleness Report — PR #{report.pr_number}",
        f"**Repo:** `{report.repo}`",
        "",
    ]

    if not report.has_stale:
        lines.append("✅ No stale labels detected.")
        return "\n".join(lines)

    lines += [
        f"### ⚠️ Stale Labels ({len(report.stale)})",
        "",
        "| Label | Applied At | Days Threshold |",
        "|-------|-----------|----------------|",
    ]
    for entry in report.stale:
        lines.append(
            f"| `{entry.label}` | {entry.applied_at.date()} | {entry.stale_after_days}d |"
        )

    if report.fresh:
        lines += [
            "",
            f"### ✅ Fresh Labels ({len(report.fresh)})",
            "",
            "| Label | Applied At | Days Threshold |",
            "|-------|-----------|----------------|",
        ]
        for entry in report.fresh:
            lines.append(
                f"| `{entry.label}` | {entry.applied_at.date()} | {entry.stale_after_days}d |"
            )

    return "\n".join(lines)


def write_staleness_summary(
    report: StalenessReport,
    summary_path: Optional[str] = None,
) -> None:
    path = summary_path or os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    markdown = render_staleness_markdown(report)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(markdown + "\n")


def log_stale_labels(report: StalenessReport) -> None:
    if report.has_stale:
        labels = ", ".join(e.label for e in report.stale)
        print(f"[staleness] stale labels on PR #{report.pr_number}: {labels}")
    else:
        print(f"[staleness] no stale labels on PR #{report.pr_number}")
