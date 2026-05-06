"""Notification module for reporting label actions applied to PRs."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LabelAction:
    label: str
    action: str  # "added" | "removed" | "skipped"
    reason: str

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "action": self.action,
            "reason": self.reason,
        }


@dataclass
class PRNotification:
    pr_number: int
    repo: str
    actions: List[LabelAction] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_action(self, label: str, action: str, reason: str) -> None:
        self.actions.append(LabelAction(label=label, action=action, reason=reason))

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "timestamp": self.timestamp,
            "actions": [a.to_dict() for a in self.actions],
        }

    def format_summary(self) -> str:
        if not self.actions:
            return f"PR #{self.pr_number}: no label changes."
        lines = [f"PR #{self.pr_number} label actions:"]
        for a in self.actions:
            lines.append(f"  [{a.action.upper()}] {a.label} — {a.reason}")
        return "\n".join(lines)


class NotificationService:
    """Logs and optionally persists PR label notifications."""

    def __init__(self, output_path: Optional[str] = None) -> None:
        self._output_path = output_path

    def send(self, notification: PRNotification) -> None:
        summary = notification.format_summary()
        logger.info(summary)
        if self._output_path:
            self._write(notification)

    def _write(self, notification: PRNotification) -> None:
        with open(self._output_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(notification.to_dict()) + "\n")
