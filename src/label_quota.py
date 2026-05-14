"""Label quota enforcement — limits the total number of labels applied to a PR."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class QuotaConfig:
    max_labels: int = 10
    overflow_strategy: str = "drop"  # "drop" | "warn"

    def __post_init__(self) -> None:
        if self.max_labels < 1:
            raise ValueError("max_labels must be at least 1")
        if self.overflow_strategy not in ("drop", "warn"):
            raise ValueError("overflow_strategy must be 'drop' or 'warn'")


@dataclass
class QuotaResult:
    allowed: List[str] = field(default_factory=list)
    dropped: List[str] = field(default_factory=list)
    warning: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "allowed": list(self.allowed),
            "dropped": list(self.dropped),
            "warning": self.warning,
        }


class LabelQuotaEnforcer:
    """Applies a quota cap to a list of candidate labels."""

    def __init__(self, config: QuotaConfig) -> None:
        self._config = config

    def enforce(self, labels: List[str]) -> QuotaResult:
        """Return a QuotaResult partitioning *labels* into allowed / dropped."""
        max_labels = self._config.max_labels
        if len(labels) <= max_labels:
            return QuotaResult(allowed=list(labels))

        allowed = labels[:max_labels]
        dropped = labels[max_labels:]
        warning: Optional[str] = None

        if self._config.overflow_strategy == "warn":
            warning = (
                f"{len(dropped)} label(s) exceed the quota of {max_labels} "
                f"and will still be applied: {dropped}"
            )
            # In warn mode we still allow everything but surface the warning.
            return QuotaResult(allowed=list(labels), dropped=[], warning=warning)

        # drop mode
        warning = (
            f"{len(dropped)} label(s) dropped due to quota limit of {max_labels}: "
            f"{dropped}"
        )
        return QuotaResult(allowed=allowed, dropped=dropped, warning=warning)
