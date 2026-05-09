"""Label expiry: automatically schedule label removal after a TTL."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ExpiryRecord:
    label: str
    pr_number: int
    expires_at: float  # unix timestamp

    def is_expired(self, now: Optional[float] = None) -> bool:
        return (now if now is not None else time.time()) >= self.expires_at

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "pr_number": self.pr_number,
            "expires_at": self.expires_at,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ExpiryRecord":
        return cls(
            label=data["label"],
            pr_number=data["pr_number"],
            expires_at=float(data["expires_at"]),
        )


class LabelExpiryStore:
    """Persist and query label expiry records backed by a JSON-lines file."""

    def __init__(self, store_path: Path) -> None:
        self._path = store_path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _read_all(self) -> List[ExpiryRecord]:
        if not self._path.exists():
            return []
        records: List[ExpiryRecord] = []
        for line in self._path.read_text().splitlines():
            line = line.strip()
            if line:
                records.append(ExpiryRecord.from_dict(json.loads(line)))
        return records

    def _write_all(self, records: List[ExpiryRecord]) -> None:
        self._path.write_text(
            "\n".join(json.dumps(r.to_dict()) for r in records) + ("\n" if records else "")
        )

    def schedule(self, label: str, pr_number: int, ttl_seconds: float) -> ExpiryRecord:
        record = ExpiryRecord(
            label=label,
            pr_number=pr_number,
            expires_at=time.time() + ttl_seconds,
        )
        records = self._read_all()
        records = [r for r in records if not (r.label == label and r.pr_number == pr_number)]
        records.append(record)
        self._write_all(records)
        return record

    def expired_for_pr(self, pr_number: int, now: Optional[float] = None) -> List[ExpiryRecord]:
        return [
            r for r in self._read_all()
            if r.pr_number == pr_number and r.is_expired(now)
        ]

    def remove(self, label: str, pr_number: int) -> None:
        records = [r for r in self._read_all() if not (r.label == label and r.pr_number == pr_number)]
        self._write_all(records)
