"""
AI Summarizer V7.8 Retry Policy
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetryPolicy:
    """
    Defines retry behavior for runtime operations.
    """

    enabled: bool = True

    max_attempts: int = 3

    delay_seconds: float = 0.0

    exponential_backoff: bool = False

    retry_exceptions: tuple[type[Exception], ...] = (Exception,)
