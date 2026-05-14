"""Render alias-resolution details for GitHub Step Summary output."""
from __future__ import annotations

import os
from typing import Dict, List

from src.label_alias import AliasMap


def render_alias_markdown(alias_map: AliasMap, resolved: Dict[str, str]) -> str:
    """Return a Markdown report describing which labels were aliased.

    Args:
        alias_map: The configured alias map.
        resolved: Mapping of original_label -> canonical_label for labels that
                  were actually resolved during a run (alias != canonical).
    """
    lines: List[str] = ["## 🏷️ Label Alias Resolution\n"]

    if not resolved:
        lines.append("_No aliases were applied in this run._\n")
        return "\n".join(lines)

    lines.append("| Original | Canonical |")
    lines.append("|----------|-----------|")
    for original, canonical in sorted(resolved.items()):
        lines.append(f"| `{original}` | `{canonical}` |")

    total = len(alias_map)
    lines.append(f"\n> {total} alias(es) configured, {len(resolved)} applied.\n")
    return "\n".join(lines)


def write_alias_summary(alias_map: AliasMap, resolved: Dict[str, str]) -> None:
    """Append the alias report to GITHUB_STEP_SUMMARY when available."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if not summary_path:
        return
    markdown = render_alias_markdown(alias_map, resolved)
    with open(summary_path, "a", encoding="utf-8") as fh:
        fh.write(markdown)
        fh.write("\n")


def log_resolutions(resolved: Dict[str, str]) -> None:
    """Print alias resolutions to stdout for Action log visibility."""
    if not resolved:
        print("[alias] No aliases applied.")
        return
    for original, canonical in sorted(resolved.items()):
        print(f"[alias] '{original}' -> '{canonical}'")
