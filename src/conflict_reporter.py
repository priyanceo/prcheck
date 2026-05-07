"""Format and report label conflict resolution outcomes."""
from typing import List

from src.label_conflict import ConflictResult


def render_conflict_markdown(pr_number: int, result: ConflictResult) -> str:
    """Render a Markdown summary of conflict resolution for a PR."""
    lines: List[str] = []
    lines.append(f"## Label Conflict Report — PR #{pr_number}")
    lines.append("")

    if not result.dropped:
        lines.append("_No label conflicts detected._")
        return "\n".join(lines)

    lines.append("### ✅ Applied Labels")
    if result.resolved:
        for label in result.resolved:
            lines.append(f"- `{label}`")
    else:
        lines.append("_None_")

    lines.append("")
    lines.append("### ⚠️ Dropped Labels (conflicts)")
    for label, reason in result.dropped.items():
        lines.append(f"- `{label}` — {reason}")

    return "\n".join(lines)


def write_conflict_summary(
    pr_number: int,
    result: ConflictResult,
    summary_path: str,
) -> None:
    """Append the conflict resolution Markdown to a step summary file."""
    content = render_conflict_markdown(pr_number, result)
    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write(content)
        fh.write("\n")


def log_conflicts(pr_number: int, result: ConflictResult) -> List[str]:
    """Return a list of human-readable log lines for conflict resolution."""
    lines: List[str] = []
    if not result.dropped:
        lines.append(f"[PR #{pr_number}] No label conflicts.")
        return lines

    for label, reason in result.dropped.items():
        lines.append(f"[PR #{pr_number}] Dropped label '{label}': {reason}")
    return lines
