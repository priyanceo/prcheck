"""Audit log for recording labeling actions applied to pull requests."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


@dataclass
class AuditEntry:
    pr_number: int
    repo: str
    labels_added: List[str]
    labels_removed: List[str]
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    triggered_by: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "pr_number": self.pr_number,
            "repo": self.repo,
            "labels_added": self.labels_added,
            "labels_removed": self.labels_removed,
            "timestamp": self.timestamp,
            "triggered_by": self.triggered_by,
        }


class AuditLog:
    """Appends JSON-line audit entries to a log file."""

    def __init__(self, log_path: str) -> None:
        self._log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True) if os.path.dirname(log_path) else None

    def record(self, entry: AuditEntry) -> None:
        """Append a single audit entry to the log file."""
        with open(self._log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry.to_dict()) + "\n")

    def read_all(self) -> List[AuditEntry]:
        """Return all entries recorded in the log file."""
        if not os.path.exists(self._log_path):
            return []
        entries: List[AuditEntry] = []
        with open(self._log_path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                entries.append(
                    AuditEntry(
                        pr_number=data["pr_number"],
                        repo=data["repo"],
                        labels_added=data["labels_added"],
                        labels_removed=data["labels_removed"],
                        timestamp=data["timestamp"],
                        triggered_by=data.get("triggered_by"),
                    )
                )
        return entries
