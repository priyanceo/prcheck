"""Collect and report run metrics for prcheck actions."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RunMetrics:
    """Holds timing and label statistics for a single action run."""

    pr_number: int
    start_time: float = field(default_factory=time.monotonic)
    end_time: float | None = None
    labels_added: List[str] = field(default_factory=list)
    labels_removed: List[str] = field(default_factory=list)
    files_evaluated: int = 0
    total_changes: int = 0

    def finish(self) -> None:
        """Record the end time of the run."""
        self.end_time = time.monotonic()

    @property
    def elapsed_seconds(self) -> float | None:
        """Return elapsed wall-clock seconds, or None if not finished."""
        if self.end_time is None:
            return None
        return self.end_time - self.start_time

    def to_dict(self) -> Dict[str, object]:
        """Serialize metrics to a plain dictionary."""
        return {
            "pr_number": self.pr_number,
            "elapsed_seconds": self.elapsed_seconds,
            "labels_added": list(self.labels_added),
            "labels_removed": list(self.labels_removed),
            "files_evaluated": self.files_evaluated,
            "total_changes": self.total_changes,
        }


def format_summary(metrics: RunMetrics) -> str:
    """Return a human-readable summary string for logging."""
    elapsed = (
        f"{metrics.elapsed_seconds:.3f}s"
        if metrics.elapsed_seconds is not None
        else "n/a"
    )
    added = ", ".join(metrics.labels_added) or "none"
    removed = ", ".join(metrics.labels_removed) or "none"
    return (
        f"PR #{metrics.pr_number} | elapsed={elapsed} "
        f"files={metrics.files_evaluated} changes={metrics.total_changes} "
        f"added=[{added}] removed=[{removed}]"
    )
