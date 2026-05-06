"""Renders a PRSummary as GitHub Actions step-summary markdown."""

from src.pr_summary import PRSummary


def _badge(label: str, color: str) -> str:
    escaped = label.replace("-", "--").replace("_", "__")
    return f"![{label}](https://img.shields.io/badge/{escaped}-{color})"


def render_markdown(summary: PRSummary) -> str:
    lines = [
        f"## prcheck — PR #{summary.pr_number}",
        "",
        f"**Repository:** `{summary.repo}`  ",
        f"**Total diff size:** {summary.total_changes} lines",
        "",
    ]

    if summary.labels_added:
        lines.append("### ✅ Labels Added")
        for lbl in summary.labels_added:
            lines.append(f"- {_badge(lbl, 'brightgreen')}")
        lines.append("")

    if summary.labels_removed:
        lines.append("### 🗑️ Labels Removed")
        for lbl in summary.labels_removed:
            lines.append(f"- {_badge(lbl, 'lightgrey')}")
        lines.append("")

    if summary.labels_skipped:
        lines.append("### ⏭️ Labels Skipped (already present)")
        for lbl in summary.labels_skipped:
            lines.append(f"- `{lbl}`")
        lines.append("")

    if summary.matched_rules:
        lines.append("### 📋 Matched Rules")
        for rule in summary.matched_rules:
            lines.append(f"- `{rule}`")
        lines.append("")

    if not summary.labels_added and not summary.labels_removed:
        lines.append("_No label changes were made._")

    return "\n".join(lines)


def write_step_summary(summary: PRSummary, output_path: str) -> None:
    """Write markdown to a file (typically $GITHUB_STEP_SUMMARY)."""
    content = render_markdown(summary)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(content)
