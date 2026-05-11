"""Scores candidate labels by confidence based on matched rules and file coverage."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LabelScore:
    label: str
    matched_files: int
    total_files: int
    rule_weight: float = 1.0

    def __post_init__(self) -> None:
        if self.total_files < 0:
            raise ValueError("total_files must be non-negative")
        if self.matched_files < 0:
            raise ValueError("matched_files must be non-negative")
        if self.matched_files > self.total_files:
            raise ValueError("matched_files cannot exceed total_files")
        if self.rule_weight <= 0:
            raise ValueError("rule_weight must be positive")

    @property
    def coverage(self) -> float:
        """Fraction of total files matched by this label's rules."""
        if self.total_files == 0:
            return 0.0
        return self.matched_files / self.total_files

    @property
    def confidence(self) -> float:
        """Weighted confidence score in [0.0, 1.0]."""
        return min(self.coverage * self.rule_weight, 1.0)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "matched_files": self.matched_files,
            "total_files": self.total_files,
            "rule_weight": self.rule_weight,
            "coverage": round(self.coverage, 4),
            "confidence": round(self.confidence, 4),
        }


@dataclass
class ScoredResult:
    scores: List[LabelScore] = field(default_factory=list)
    threshold: float = 0.0

    def above_threshold(self) -> List[LabelScore]:
        """Return scores whose confidence meets or exceeds the threshold."""
        return [s for s in self.scores if s.confidence >= self.threshold]

    def top(self, n: int = 5) -> List[LabelScore]:
        """Return top-n scores sorted by confidence descending."""
        return sorted(self.scores, key=lambda s: s.confidence, reverse=True)[:n]

    def to_dict(self) -> dict:
        return {
            "threshold": self.threshold,
            "scores": [s.to_dict() for s in self.scores],
        }
