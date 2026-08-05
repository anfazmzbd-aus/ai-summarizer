"""
Retry policy.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RetryPolicy:

    max_attempts: int = 3
