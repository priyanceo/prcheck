"""Retry utility with exponential backoff for GitHub API calls."""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Callable, Tuple, Type

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    max_attempts: int = 3
    base_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 30.0
    retryable_exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (IOError, TimeoutError)
    )


def with_retry(fn: Callable, config: RetryConfig | None = None):
    """Call *fn* with exponential backoff retries.

    Returns the result of *fn* on success, or re-raises the last exception
    after all attempts are exhausted.
    """
    if config is None:
        config = RetryConfig()

    last_exc: Exception | None = None
    delay = config.base_delay

    for attempt in range(1, config.max_attempts + 1):
        try:
            return fn()
        except config.retryable_exceptions as exc:  # type: ignore[misc]
            last_exc = exc
            if attempt == config.max_attempts:
                logger.error(
                    "All %d attempts failed: %s", config.max_attempts, exc
                )
                raise
            sleep_time = min(delay, config.max_delay)
            logger.warning(
                "Attempt %d/%d failed (%s). Retrying in %.1fs…",
                attempt,
                config.max_attempts,
                exc,
                sleep_time,
            )
            time.sleep(sleep_time)
            delay *= config.backoff_factor

    raise RuntimeError("Unreachable")  # pragma: no cover
