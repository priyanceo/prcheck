"""Rate-limiting / throttle guard for label operations.

Prevents the same label from being applied or removed on a given PR
more than *max_operations* times within a rolling *window_seconds* window.
This avoids runaway re-labelling when a PR is updated rapidly.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class ThrottleConfig:
    window_seconds: int = 3600
    max_operations: int = 5


@dataclass
class _LabelRecord:
    timestamps: List[float] = field(default_factory=list)

    def prune(self, window_seconds: int) -> None:
        cutoff = time.time() - window_seconds
        self.timestamps = [t for t in self.timestamps if t >= cutoff]

    def count(self) -> int:
        return len(self.timestamps)

    def record(self) -> None:
        self.timestamps.append(time.time())


class LabelThrottle:
    """Persist per-label operation counts and enforce throttle limits."""

    def __init__(self, store_path: Path, config: ThrottleConfig | None = None) -> None:
        self._path = store_path
        self._config = config or ThrottleConfig()
        self._data: Dict[str, _LabelRecord] = {}
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_allowed(self, label: str) -> bool:
        """Return True if the operation is within the throttle limit."""
        rec = self._data.get(label, _LabelRecord())
        rec.prune(self._config.window_seconds)
        return rec.count() < self._config.max_operations

    def record_operation(self, label: str) -> None:
        """Record that an operation was performed for *label*."""
        rec = self._data.setdefault(label, _LabelRecord())
        rec.prune(self._config.window_seconds)
        rec.record()
        self._save()

    def remaining(self, label: str) -> int:
        """Return how many more operations are allowed in the current window."""
        rec = self._data.get(label, _LabelRecord())
        rec.prune(self._config.window_seconds)
        return max(0, self._config.max_operations - rec.count())

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw: Dict[str, List[float]] = json.loads(self._path.read_text())
        self._data = {label: _LabelRecord(ts) for label, ts in raw.items()}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {label: rec.timestamps for label, rec in self._data.items()}
        self._path.write_text(json.dumps(payload))
