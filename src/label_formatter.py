"""Utilities for formatting and normalizing label names."""
from __future__ import annotations

import re
from dataclasses import dataclass


_WHITESPACE_RE = re.compile(r"[\s_]+")
_INVALID_CHARS_RE = re.compile(r"[^a-z0-9:/@.\-]")


@dataclass(frozen=True)
class FormattedLabel:
    """A normalized label name together with its original raw value."""

    raw: str
    normalized: str

    def __str__(self) -> str:  # pragma: no cover
        return self.normalized


def normalize(label: str) -> str:
    """Return a normalized version of *label*.

    Rules applied in order:
    1. Strip leading/trailing whitespace.
    2. Convert to lower-case.
    3. Replace runs of whitespace or underscores with a single hyphen.
    4. Remove any remaining characters that are not alphanumeric or one of
       the special characters GitHub allows in label names (: / @ . -).
    5. Strip any leading or trailing hyphens produced by the previous steps.
    """
    if not isinstance(label, str):
        raise TypeError(f"label must be a str, got {type(label).__name__!r}")

    result = label.strip()
    result = result.lower()
    result = _WHITESPACE_RE.sub("-", result)
    result = _INVALID_CHARS_RE.sub("", result)
    result = result.strip("-")
    return result


def format_label(label: str) -> FormattedLabel:
    """Return a :class:`FormattedLabel` for *label*."""
    return FormattedLabel(raw=label, normalized=normalize(label))


def format_labels(labels: list[str]) -> list[FormattedLabel]:
    """Return a list of :class:`FormattedLabel` objects for each entry in *labels*."""
    return [format_label(lbl) for lbl in labels]


def deduplicate(labels: list[str]) -> list[str]:
    """Return *labels* with duplicates removed (case-insensitive, order preserved)."""
    seen: set[str] = set()
    result: list[str] = []
    for lbl in labels:
        key = normalize(lbl)
        if key not in seen:
            seen.add(key)
            result.append(lbl)
    return result
