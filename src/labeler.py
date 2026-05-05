"""Core labeling logic for prcheck GitHub Action."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LabelRule:
    """A single label rule mapping a glob pattern to a label name."""

    label: str
    patterns: List[str]

    def matches(self, filepath: str) -> bool:
        """Return True if *filepath* matches any of the rule's glob patterns."""
        return any(fnmatch.fnmatch(filepath, pattern) for pattern in self.patterns)


@dataclass
class SizeRule:
    """A label rule based on the total diff size (lines changed)."""

    label: str
    min_lines: int = 0
    max_lines: Optional[int] = None

    def __post_init__(self) -> None:
        """Validate that min_lines and max_lines form a sensible range."""
        if self.min_lines < 0:
            raise ValueError(f"min_lines must be >= 0, got {self.min_lines}")
        if self.max_lines is not None and self.max_lines < self.min_lines:
            raise ValueError(
                f"max_lines ({self.max_lines}) must be >= min_lines ({self.min_lines})"
            )

    def matches(self, total_lines: int) -> bool:
        """Return True if *total_lines* falls within [min_lines, max_lines]."""
        if total_lines < self.min_lines:
            return False
        if self.max_lines is not None and total_lines > self.max_lines:
            return False
        return True


@dataclass
class Labeler:
    """Determines which labels to apply given changed files and diff size."""

    path_rules: List[LabelRule] = field(default_factory=list)
    size_rules: List[SizeRule] = field(default_factory=list)

    def labels_for_paths(self, changed_files: List[str]) -> List[str]:
        """Return labels whose path rules match at least one changed file."""
        matched: list[str] = []
        for rule in self.path_rules:
            if any(rule.matches(f) for f in changed_files):
                if rule.label not in matched:
                    matched.append(rule.label)
        return matched

    def labels_for_size(self, total_lines: int) -> List[str]:
        """Return labels whose size rules match *total_lines*."""
        return [
            rule.label
            for rule in self.size_rules
            if rule.matches(total_lines)
        ]

    def compute_labels(
        self,
        changed_files: List[str],
        total_lines: int,
    ) -> List[str]:
        """Return the full deduplicated list of labels to apply."""
        labels = self.labels_for_paths(changed_files)
        for label in self.labels_for_size(total_lines):
            if label not in labels:
                labels.append(label)
        return labels
