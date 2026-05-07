"""Tracks the history of label changes applied to a PR across runs."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


@dataclass
class LabelEvent:
    label: str
    action: str  # "added" | "removed" | "skipped"
    reason: str
    run_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "action": self.action,
            "reason": self.reason,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
        }

    @staticmethod
    def from_dict(data: dict) -> "LabelEvent":
        return LabelEvent(
            label=data["label"],
            action=data["action"],
            reason=data["reason"],
            run_id=data["run_id"],
            timestamp=data["timestamp"],
        )


class LabelHistory:
    def __init__(self, history_path: Path) -> None:
        self._path = history_path
        self._events: List[LabelEvent] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        self._events.append(LabelEvent.from_dict(json.loads(line)))
                    except (KeyError, json.JSONDecodeError):
                        pass

    def record(self, event: LabelEvent) -> None:
        self._events.append(event)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.to_dict()) + "\n")

    def all_events(self) -> List[LabelEvent]:
        return list(self._events)

    def events_for_label(self, label: str) -> List[LabelEvent]:
        return [e for e in self._events if e.label == label]

    def last_action_for_label(self, label: str) -> Optional[LabelEvent]:
        matches = self.events_for_label(label)
        return matches[-1] if matches else None
