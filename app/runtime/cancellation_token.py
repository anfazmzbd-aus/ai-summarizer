"""
AI Summarizer V7.8 Runtime Cancellation Token

Provides cooperative cancellation support for runtime executions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CancellationToken:
    """
    Cooperative cancellation token.

    Long-running runtime components periodically check this token
    to determine whether execution should stop gracefully.
    """

    _cancelled: bool = False

    def cancel(self) -> None:
        """
        Request cancellation.
        """
        self._cancelled = True

    @property
    def cancelled(self) -> bool:
        """
        Returns True if cancellation has been requested.
        """
        return self._cancelled

    def is_cancelled(self) -> bool:
        """
        Convenience helper.
        """
        return self._cancelled
