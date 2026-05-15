"""Label pinning: prevent specific labels from being removed by automation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import FrozenSet, List, Set


@dataclass(frozen=True)
class PinConfig:
    """Configuration for pinned labels."""

    pinned: FrozenSet[str] = field(default_factory=frozenset)

    def is_pinned(self, label: str) -> bool:
        """Return True if *label* is pinned and must not be removed."""
        return label.strip().lower() in self.pinned


@dataclass
class PinResult:
    """Outcome of a pin-check for a set of candidate removals."""

    blocked: List[str] = field(default_factory=list)
    allowed: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"blocked": list(self.blocked), "allowed": list(self.allowed)}


class LabelPinEnforcer:
    """Filter out pinned labels from a proposed removal list."""

    def __init__(self, config: PinConfig) -> None:
        self._config = config

    def check_removals(self, labels: List[str]) -> PinResult:
        """Split *labels* into blocked (pinned) and allowed (removable) sets."""
        result = PinResult()
        for label in labels:
            if self._config.is_pinned(label):
                result.blocked.append(label)
            else:
                result.allowed.append(label)
        return result

    def filter_removals(self, labels: List[str]) -> List[str]:
        """Return only those labels that are *not* pinned."""
        return self.check_removals(labels).allowed


def parse_pin_config(raw: dict) -> PinConfig:
    """Build a :class:`PinConfig` from the top-level config mapping."""
    section = raw.get("pin", {})
    if not isinstance(section, dict):
        return PinConfig()
    raw_list = section.get("labels", [])
    if not isinstance(raw_list, list):
        return PinConfig()
    pinned: Set[str] = set()
    for item in raw_list:
        if isinstance(item, str) and item.strip():
            pinned.add(item.strip().lower())
    return PinConfig(pinned=frozenset(pinned))
