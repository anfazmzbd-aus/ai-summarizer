"""
AI Summarizer V8.0 Distributed Runtime

Retry policy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RetryPolicy:
    """
    Retry configuration.
    """

    max_attempts: int = 3

    backoff_seconds: float = 5.0

    exponential_backoff: bool = True

    def should_retry(
        self,
        retry_count: int,
    ) -> bool:

        return retry_count < self.max_attempts

    def next_delay(
        self,
        retry_count: int,
    ) -> float:

        if not self.exponential_backoff:

            return self.backoff_seconds

        return self.backoff_seconds * (2**retry_count)
