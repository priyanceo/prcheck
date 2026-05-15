"""Label lifecycle management: track created/updated/removed timestamps per label per PR."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class LifecycleEvent:
    label: str
    event: str  # "created" | "updated" | "removed"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    pr_number: int = 0

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "event": self.event,
            "timestamp": self.timestamp,
            "pr_number": self.pr_number,
        }

    @staticmethod
    def from_dict(data: dict) -> "LifecycleEvent":
        return LifecycleEvent(
            label=data["label"],
            event=data["event"],
            timestamp=data["timestamp"],
            pr_number=data.get("pr_number", 0),
        )


class LabelLifecycleStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._events: List[LifecycleEvent] = []
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            raw = self._path.read_text(encoding="utf-8").strip()
            for line in raw.splitlines():
                try:
                    self._events.append(LifecycleEvent.from_dict(json.loads(line)))
                except (KeyError, json.JSONDecodeError):
                    pass

    def record(self, label: str, event: str, pr_number: int = 0) -> LifecycleEvent:
        if event not in ("created", "updated", "removed"):
            raise ValueError(f"Unknown lifecycle event: {event!r}")
        entry = LifecycleEvent(label=label, event=event, pr_number=pr_number)
        self._events.append(entry)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict()) + "\n")
        return entry

    def events_for(self, label: str) -> List[LifecycleEvent]:
        return [e for e in self._events if e.label == label]

    def latest_event(self, label: str) -> Optional[LifecycleEvent]:
        matches = self.events_for(label)
        return matches[-1] if matches else None

    def all_events(self) -> List[LifecycleEvent]:
        return list(self._events)
