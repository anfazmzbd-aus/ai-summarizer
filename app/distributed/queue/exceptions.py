"""
AI Summarizer V8.0 Distributed Runtime

Queue related exceptions.
"""

from __future__ import annotations


class QueueError(Exception):
    """Base queue exception."""


class QueueEmptyError(QueueError):
    """Raised when queue has no available tasks."""


class QueueFullError(QueueError):
    """Raised when queue capacity is exceeded."""


class QueueConnectionError(QueueError):
    """Raised when external queue connection fails."""
