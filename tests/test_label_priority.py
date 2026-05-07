"""Tests for LabelPriorityResolver and PriorityRule."""
import pytest

from src.label_priority import LabelPriorityResolver, PriorityResult, PriorityRule


# ---------------------------------------------------------------------------
# PriorityRule
# ---------------------------------------------------------------------------

class TestPriorityRule:
    def test_valid_rule(self):
        r = PriorityRule(label="bug", priority=10)
        assert r.label == "bug"
        assert r.priority == 10

    def test_default_priority_is_zero(self):
        r = PriorityRule(label="docs")
        assert r.priority == 0

    def test_empty_label_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            PriorityRule(label="")

    def test_blank_label_raises(self):
        with pytest.raises(ValueError, match="non-empty"):
            PriorityRule(label="   ")

    def test_non_int_priority_raises(self):
        with pytest.raises(ValueError, match="integer"):
            PriorityRule(label="bug", priority="high")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# LabelPriorityResolver
# ---------------------------------------------------------------------------

def _make_resolver(max_labels=None):
    rules = [
        PriorityRule(label="critical", priority=100),
        PriorityRule(label="bug", priority=50),
        PriorityRule(label="enhancement", priority=10),
    ]
    return LabelPriorityResolver(rules=rules, max_labels=max_labels)


class TestLabelPriorityResolver:
    def test_sorts_by_priority_descending(self):
        resolver = _make_resolver()
        result = resolver.resolve(["enhancement", "critical", "bug"])
        assert result.ordered == ["critical", "bug", "enhancement"]

    def test_unknown_labels_get_priority_zero(self):
        resolver = _make_resolver()
        result = resolver.resolve(["unknown", "bug"])
        assert result.ordered[0] == "bug"
        assert "unknown" in result.ordered

    def test_no_max_labels_drops_nothing(self):
        resolver = _make_resolver(max_labels=None)
        result = resolver.resolve(["bug", "enhancement", "critical"])
        assert result.dropped == []
        assert len(result.ordered) == 3

    def test_max_labels_caps_output(self):
        resolver = _make_resolver(max_labels=2)
        result = resolver.resolve(["enhancement", "critical", "bug"])
        assert result.ordered == ["critical", "bug"]
        assert result.dropped == ["enhancement"]

    def test_max_labels_zero_drops_all(self):
        resolver = _make_resolver(max_labels=0)
        result = resolver.resolve(["bug", "critical"])
        assert result.ordered == []
        assert set(result.dropped) == {"bug", "critical"}

    def test_empty_labels_returns_empty(self):
        resolver = _make_resolver(max_labels=3)
        result = resolver.resolve([])
        assert result.ordered == []
        assert result.dropped == []

    def test_to_dict_shape(self):
        resolver = _make_resolver(max_labels=1)
        result = resolver.resolve(["bug", "critical"])
        d = result.to_dict()
        assert "ordered" in d
        assert "dropped" in d
