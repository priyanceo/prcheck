"""Filter labels based on allow/deny lists and protection rules."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LabelFilterConfig:
    allow_list: list[str] = field(default_factory=list)
    deny_list: list[str] = field(default_factory=list)
    protected_labels: list[str] = field(default_factory=list)


@dataclass
class FilterResult:
    label: str
    allowed: bool
    reason: str

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "allowed": self.allowed,
            "reason": self.reason,
        }


class LabelFilter:
    """Decides which labels may be added or removed given a filter config."""

    def __init__(self, config: LabelFilterConfig) -> None:
        self._config = config

    def check_add(self, label: str) -> FilterResult:
        """Return a FilterResult indicating whether *label* may be added."""
        if self._config.allow_list and label not in self._config.allow_list:
            return FilterResult(label=label, allowed=False, reason="not in allow_list")
        if label in self._config.deny_list:
            return FilterResult(label=label, allowed=False, reason="in deny_list")
        return FilterResult(label=label, allowed=True, reason="ok")

    def check_remove(self, label: str) -> FilterResult:
        """Return a FilterResult indicating whether *label* may be removed."""
        if label in self._config.protected_labels:
            return FilterResult(label=label, allowed=False, reason="protected")
        return FilterResult(label=label, allowed=True, reason="ok")

    def filter_additions(self, labels: list[str]) -> list[str]:
        """Return only the labels from *labels* that are allowed to be added."""
        return [lbl for lbl in labels if self.check_add(lbl).allowed]

    def filter_removals(self, labels: list[str]) -> list[str]:
        """Return only the labels from *labels* that are allowed to be removed."""
        return [lbl for lbl in labels if self.check_remove(lbl).allowed]


def parse_label_filter_config(raw: dict) -> LabelFilterConfig:
    """Build a LabelFilterConfig from a raw mapping (e.g. parsed YAML)."""
    section: dict = raw.get("label_filter", {})
    return LabelFilterConfig(
        allow_list=list(section.get("allow", [])),
        deny_list=list(section.get("deny", [])),
        protected_labels=list(section.get("protected", [])),
    )
