"""Tests for src/retry.py"""

import pytest
from unittest.mock import MagicMock, patch

from src.retry import RetryConfig, with_retry


class TestRetryConfigDefaults:
    def test_default_max_attempts(self):
        cfg = RetryConfig()
        assert cfg.max_attempts == 3

    def test_default_base_delay(self):
        cfg = RetryConfig()
        assert cfg.base_delay == 1.0

    def test_default_backoff_factor(self):
        cfg = RetryConfig()
        assert cfg.backoff_factor == 2.0

    def test_default_max_delay(self):
        cfg = RetryConfig()
        assert cfg.max_delay == 30.0


class TestWithRetry:
    def _cfg(self, attempts=3, base_delay=0.0):
        return RetryConfig(
            max_attempts=attempts,
            base_delay=base_delay,
            retryable_exceptions=(ValueError,),
        )

    def test_returns_value_on_first_success(self):
        fn = MagicMock(return_value=42)
        result = with_retry(fn, self._cfg())
        assert result == 42
        fn.assert_called_once()

    def test_retries_on_retryable_exception(self):
        fn = MagicMock(side_effect=[ValueError("boom"), 99])
        with patch("src.retry.time.sleep"):
            result = with_retry(fn, self._cfg())
        assert result == 99
        assert fn.call_count == 2

    def test_raises_after_max_attempts(self):
        fn = MagicMock(side_effect=ValueError("always fails"))
        with patch("src.retry.time.sleep"):
            with pytest.raises(ValueError, match="always fails"):
                with_retry(fn, self._cfg(attempts=3))
        assert fn.call_count == 3

    def test_non_retryable_exception_propagates_immediately(self):
        fn = MagicMock(side_effect=RuntimeError("fatal"))
        with pytest.raises(RuntimeError, match="fatal"):
            with_retry(fn, self._cfg())
        fn.assert_called_once()

    def test_sleep_called_between_attempts(self):
        fn = MagicMock(side_effect=[ValueError(), ValueError(), 1])
        with patch("src.retry.time.sleep") as mock_sleep:
            with_retry(fn, RetryConfig(max_attempts=3, base_delay=1.0, backoff_factor=2.0, retryable_exceptions=(ValueError,)))
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)

    def test_delay_capped_at_max_delay(self):
        fn = MagicMock(side_effect=[ValueError(), ValueError(), 1])
        cfg = RetryConfig(
            max_attempts=3,
            base_delay=100.0,
            backoff_factor=2.0,
            max_delay=5.0,
            retryable_exceptions=(ValueError,),
        )
        with patch("src.retry.time.sleep") as mock_sleep:
            with_retry(fn, cfg)
        for call in mock_sleep.call_args_list:
            assert call.args[0] <= 5.0

    def test_uses_default_config_when_none_provided(self):
        fn = MagicMock(return_value="ok")
        result = with_retry(fn)
        assert result == "ok"
