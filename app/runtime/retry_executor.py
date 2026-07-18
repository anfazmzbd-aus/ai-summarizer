"""
AI Summarizer V7.8 Retry Executor
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from .backoff import Backoff
from .retry_policy import RetryPolicy


class RetryExecutor:
    """
    Executes a callable using a retry policy.
    """

    def __init__(
        self,
        policy: RetryPolicy,
    ) -> None:

        self.policy = policy

    def run(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:

        attempts = 0

        while True:

            attempts += 1

            try:
                return func(*args, **kwargs)

            except self.policy.retry_exceptions:

                if not self.policy.enabled or attempts >= self.policy.max_attempts:
                    raise

                delay = Backoff.delay(
                    attempt=attempts,
                    base_delay=self.policy.delay_seconds,
                    exponential=self.policy.exponential_backoff,
                )

                if delay > 0:
                    time.sleep(delay)
