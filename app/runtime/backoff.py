"""
AI Summarizer V7.8 Backoff Strategy
"""

from __future__ import annotations


class Backoff:
    """
    Computes retry delays.
    """

    @staticmethod
    def delay(
        attempt: int,
        base_delay: float,
        exponential: bool,
    ) -> float:

        if base_delay <= 0:
            return 0.0

        if not exponential:
            return base_delay

        return base_delay * (2 ** (attempt - 1))
