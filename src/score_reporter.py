"""Formats and writes label scoring results for GitHub Actions step summaries."""

from __future__ import annotations

import os
from typing import Dict, List

from src.label_scorer import LabelScore


def render_score_markdown(
    pr_number: int,
    repo: str,
    scores: Dict[str, LabelScore],
    min_confidence: float = 0.0,
) -> str:
    """Render a Markdown table summarising per-label scores.

    Args:
        pr_number: The pull-request number being processed.
        repo: The repository slug (owner/name).
        scores: Mapping of label name to its computed LabelScore.
        min_confidence: Scores below this threshold are flagged as low-confidence.

    Returns:
        A Markdown string ready to be written to a step summary.
    """
    lines: List[str] = [
        f"## 🏷️ Label Scores — PR #{pr_number}",
        f"**Repository:** `{repo}`",
        "",
    ]

    if not scores:
        lines.append("_No labels were scored for this pull request._")
        return "\n".join(lines)

    # Table header
    lines += [
        "| Label | Coverage | Confidence | Matched Files | Status |",
        "|-------|----------|------------|---------------|--------|",
    ]

    for label, score in sorted(scores.items()):
        coverage_pct = f"{score.coverage * 100:.1f}%"
        confidence_pct = f"{score.confidence * 100:.1f}%"
        matched = score.matched_files
        total = score.total_files
        file_info = f"{matched} / {total}"

        if score.confidence < min_confidence:
            status = "⚠️ Low confidence"
        elif score.confidence >= 0.8:
            status = "✅ Strong"
        elif score.confidence >= 0.5:
            status = "🔵 Moderate"
        else:
            status = "🟡 Weak"

        lines.append(
            f"| `{label}` | {coverage_pct} | {confidence_pct} | {file_info} | {status} |"
        )

    lines.append("")
    lines.append(
        "> Coverage = fraction of changed files matched by the rule.  "
        "Confidence = coverage weighted by match quality."
    )

    return "\n".join(lines)


def write_score_summary(
    pr_number: int,
    repo: str,
    scores: Dict[str, LabelScore],
    min_confidence: float = 0.0,
) -> None:
    """Write the score Markdown to the GitHub Actions step-summary file.

    If the ``GITHUB_STEP_SUMMARY`` environment variable is not set the output
    is silently skipped so the function is safe to call in local runs.

    Args:
        pr_number: The pull-request number being processed.
        repo: The repository slug (owner/name).
        scores: Mapping of label name to its computed LabelScore.
        min_confidence: Scores below this threshold are flagged as low-confidence.
    """
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    markdown = render_score_markdown(pr_number, repo, scores, min_confidence)
    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write(markdown)
        fh.write("\n")


def log_scores(scores: Dict[str, LabelScore], min_confidence: float = 0.0) -> None:
    """Print a compact score summary to stdout for CI log visibility.

    Args:
        scores: Mapping of label name to its computed LabelScore.
        min_confidence: Scores below this threshold trigger a warning line.
    """
    if not scores:
        print("[score_reporter] No label scores to report.")
        return

    for label, score in sorted(scores.items()):
        flag = " [LOW CONFIDENCE]" if score.confidence < min_confidence else ""
        print(
            f"[score_reporter] {label}: "
            f"coverage={score.coverage:.2f} "
            f"confidence={score.confidence:.2f} "
            f"files={score.matched_files}/{score.total_files}"
            f"{flag}"
        )
