"""Render cooldown check results as Markdown and log helpers."""
from __future__ import annotations

import os
from typing import List

from src.label_cooldown import CooldownResult


def render_cooldown_markdown(pr_number: int, results: List[CooldownResult]) -> str:
    blocked = [r for r in results if not r.allowed]
    lines = [f"## :snowflake: Label Cooldown — PR #{pr_number}", ""]

    if not blocked:
        lines.append("All labels are past their cooldown window. :white_check_mark:")
        return "\n".join(lines)

    lines.append(f"**{len(blocked)} label(s) are still in cooldown:**", )
    lines.append("")
    lines.append("| Label | Remaining (s) |")
    lines.append("|-------|--------------|")
    for r in blocked:
        lines.append(f"| `{r.label}` | {r.remaining_seconds:.0f} |")

    return "\n".join(lines)


def write_cooldown_summary(pr_number: int, results: List[CooldownResult]) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    md = render_cooldown_markdown(pr_number, results)
    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write(md + "\n")


def log_cooldown_blocks(results: List[CooldownResult]) -> None:
    blocked = [r for r in results if not r.allowed]
    for r in blocked:
        print(
            f"[prcheck] cooldown: '{r.label}' blocked — "
            f"{r.remaining_seconds:.0f}s remaining"
        )
