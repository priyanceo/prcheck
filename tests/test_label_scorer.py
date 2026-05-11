"""Tests for src/label_scorer.py."""
import pytest
from src.label_scorer import LabelScore, ScoredResult


class TestLabelScore:
    def test_coverage_zero_when_no_files(self):
        s = LabelScore(label="backend", matched_files=0, total_files=0)
        assert s.coverage == 0.0

    def test_coverage_full_match(self):
        s = LabelScore(label="backend", matched_files=5, total_files=5)
        assert s.coverage == 1.0

    def test_coverage_partial(self):
        s = LabelScore(label="backend", matched_files=2, total_files=8)
        assert s.coverage == pytest.approx(0.25)

    def test_confidence_capped_at_one(self):
        s = LabelScore(label="x", matched_files=5, total_files=5, rule_weight=10.0)
        assert s.confidence == 1.0

    def test_confidence_applies_weight(self):
        s = LabelScore(label="x", matched_files=1, total_files=4, rule_weight=2.0)
        assert s.confidence == pytest.approx(0.5)

    def test_invalid_negative_total_raises(self):
        with pytest.raises(ValueError, match="total_files"):
            LabelScore(label="x", matched_files=0, total_files=-1)

    def test_invalid_negative_matched_raises(self):
        with pytest.raises(ValueError, match="matched_files"):
            LabelScore(label="x", matched_files=-1, total_files=5)

    def test_matched_exceeds_total_raises(self):
        with pytest.raises(ValueError):
            LabelScore(label="x", matched_files=6, total_files=5)

    def test_non_positive_weight_raises(self):
        with pytest.raises(ValueError, match="rule_weight"):
            LabelScore(label="x", matched_files=1, total_files=5, rule_weight=0.0)

    def test_to_dict_keys(self):
        s = LabelScore(label="docs", matched_files=3, total_files=10)
        d = s.to_dict()
        assert set(d.keys()) == {"label", "matched_files", "total_files", "rule_weight", "coverage", "confidence"}

    def test_to_dict_values(self):
        s = LabelScore(label="docs", matched_files=3, total_files=10)
        d = s.to_dict()
        assert d["label"] == "docs"
        assert d["coverage"] == pytest.approx(0.3)


class TestScoredResult:
    def _make_scores(self):
        return [
            LabelScore(label="a", matched_files=1, total_files=10),
            LabelScore(label="b", matched_files=5, total_files=10),
            LabelScore(label="c", matched_files=3, total_files=10),
        ]

    def test_above_threshold_filters_correctly(self):
        result = ScoredResult(scores=self._make_scores(), threshold=0.4)
        labels = [s.label for s in result.above_threshold()]
        assert "b" in labels
        assert "a" not in labels

    def test_above_threshold_includes_equal(self):
        result = ScoredResult(scores=self._make_scores(), threshold=0.3)
        labels = [s.label for s in result.above_threshold()]
        assert "c" in labels

    def test_top_returns_sorted_descending(self):
        result = ScoredResult(scores=self._make_scores())
        top = result.top(2)
        assert top[0].label == "b"
        assert top[1].label == "c"

    def test_top_respects_n(self):
        result = ScoredResult(scores=self._make_scores())
        assert len(result.top(1)) == 1

    def test_to_dict_contains_scores(self):
        result = ScoredResult(scores=self._make_scores(), threshold=0.1)
        d = result.to_dict()
        assert "scores" in d
        assert len(d["scores"]) == 3
        assert d["threshold"] == 0.1
