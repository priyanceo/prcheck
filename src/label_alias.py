"""Label alias resolution: map legacy or alternate label names to canonical ones."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class AliasMap:
    """Holds alias -> canonical label mappings."""

    _aliases: Dict[str, str] = field(default_factory=dict)

    def add(self, alias: str, canonical: str) -> None:
        """Register an alias pointing to a canonical label."""
        alias = alias.strip()
        canonical = canonical.strip()
        if not alias:
            raise ValueError("alias must not be blank")
        if not canonical:
            raise ValueError("canonical label must not be blank")
        self._aliases[alias] = canonical

    def resolve(self, label: str) -> str:
        """Return the canonical label for *label*, or *label* itself if no alias exists."""
        return self._aliases.get(label, label)

    def resolve_all(self, labels: List[str]) -> List[str]:
        """Resolve every label in *labels* and deduplicate while preserving order."""
        seen: List[str] = []
        for lbl in labels:
            canonical = self.resolve(lbl)
            if canonical not in seen:
                seen.append(canonical)
        return seen

    def aliases_for(self, canonical: str) -> List[str]:
        """Return all aliases that point to *canonical*."""
        return [alias for alias, target in self._aliases.items() if target == canonical]

    def all_mappings(self) -> Dict[str, str]:
        """Return a copy of the internal alias mapping."""
        return dict(self._aliases)

    def __len__(self) -> int:
        return len(self._aliases)
