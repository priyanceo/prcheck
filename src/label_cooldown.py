"""Label cooldown enforcement — prevents a label from being re-applied
within a configurable window after it was last removed."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class CooldownConfig:
    """Per-label (or global) cooldown settings."""
    default_seconds: int = 0
    per_label: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.default_seconds < 0:
            raise ValueError("default_seconds must be >= 0")
        for label, secs in self.per_label.items():
            if secs < 0:
                raise ValueError(f"cooldown for '{label}' must be >= 0")

    def seconds_for(self, label: str) -> int:
        return self.per_label.get(label.strip().lower(), self.default_seconds)


@dataclass
class CooldownResult:
    label: str
    allowed: bool
    remaining_seconds: float = 0.0

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "allowed": self.allowed,
            "remaining_seconds": round(self.remaining_seconds, 2),
        }


class LabelCooldownStore:
    """Persists the timestamp of the last *removal* for each label."""

    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._data: Dict[str, float] = self._load()

    # ------------------------------------------------------------------
    def _load(self) -> Dict[str, float]:
        if self._path.exists():
            try:
                return json.loads(self._path.read_text())
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data))

    # ------------------------------------------------------------------
    def record_removal(self, label: str) -> None:
        self._data[label.strip().lower()] = time.time()
        self._save()

    def last_removed_at(self, label: str) -> Optional[float]:
        return self._data.get(label.strip().lower())

    def check(self, label: str, config: CooldownConfig) -> CooldownResult:
        window = config.seconds_for(label)
        if window == 0:
            return CooldownResult(label=label, allowed=True)
        last = self.last_removed_at(label)
        if last is None:
            return CooldownResult(label=label, allowed=True)
        elapsed = time.time() - last
        if elapsed >= window:
            return CooldownResult(label=label, allowed=True)
        return CooldownResult(
            label=label,
            allowed=False,
            remaining_seconds=window - elapsed,
        )
