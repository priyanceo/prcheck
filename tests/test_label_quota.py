"""Tests for src/label_quota.py."""
import pytest

from src.label_quota import LabelQuotaEnforcer, QuotaConfig, QuotaResult


def _make_enforcer(max_labels: int = 3, strategy: str = "drop") -> LabelQuotaEnforcer:
    return LabelQuotaEnforcer(QuotaConfig(max_labels=max_labels, overflow_strategy=strategy))


class TestQuotaConfig:
    def test_valid_config(self):
        cfg = QuotaConfig(max_labels=5, overflow_strategy="warn")
        assert cfg.max_labels == 5
        assert cfg.overflow_strategy == "warn"

    def test_max_labels_below_one_raises(self):
        with pytest.raises(ValueError, match="max_labels"):
            QuotaConfig(max_labels=0)

    def test_invalid_strategy_raises(self):
        with pytest.raises(ValueError, match="overflow_strategy"):
            QuotaConfig(overflow_strategy="ignore")


class TestQuotaResult:
    def test_to_dict_contains_expected_keys(self):
        result = QuotaResult(allowed=["bug"], dropped=["size:xl"], warning="too many")
        d = result.to_dict()
        assert set(d.keys()) == {"allowed", "dropped", "warning"}

    def test_to_dict_values(self):
        result = QuotaResult(allowed=["a"], dropped=["b"], warning=None)
        assert result.to_dict()["allowed"] == ["a"]
        assert result.to_dict()["dropped"] == ["b"]
        assert result.to_dict()["warning"] is None


class TestEnforceDrop:
    def test_within_quota_all_allowed(self):
        enforcer = _make_enforcer(max_labels=5)
        result = enforcer.enforce(["a", "b", "c"])
        assert result.allowed == ["a", "b", "c"]
        assert result.dropped == []
        assert result.warning is None

    def test_exactly_at_quota_all_allowed(self):
        enforcer = _make_enforcer(max_labels=3)
        result = enforcer.enforce(["a", "b", "c"])
        assert len(result.allowed) == 3
        assert result.dropped == []

    def test_over_quota_drops_excess(self):
        enforcer = _make_enforcer(max_labels=2)
        result = enforcer.enforce(["a", "b", "c", "d"])
        assert result.allowed == ["a", "b"]
        assert result.dropped == ["c", "d"]

    def test_over_quota_sets_warning(self):
        enforcer = _make_enforcer(max_labels=1)
        result = enforcer.enforce(["x", "y"])
        assert result.warning is not None
        assert "y" in result.warning

    def test_empty_labels_returns_empty_allowed(self):
        enforcer = _make_enforcer(max_labels=3)
        result = enforcer.enforce([])
        assert result.allowed == []
        assert result.dropped == []


class TestEnforceWarn:
    def test_over_quota_all_still_allowed(self):
        enforcer = _make_enforcer(max_labels=2, strategy="warn")
        result = enforcer.enforce(["a", "b", "c"])
        assert result.allowed == ["a", "b", "c"]
        assert result.dropped == []

    def test_over_quota_warning_mentions_excess(self):
        enforcer = _make_enforcer(max_labels=2, strategy="warn")
        result = enforcer.enforce(["a", "b", "c"])
        assert result.warning is not None
        assert "c" in result.warning

    def test_within_quota_no_warning(self):
        enforcer = _make_enforcer(max_labels=5, strategy="warn")
        result = enforcer.enforce(["a", "b"])
        assert result.warning is None
