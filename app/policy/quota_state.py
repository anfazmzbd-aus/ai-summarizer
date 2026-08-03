"""
Current runtime quota state.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class QuotaState:

    queue_depth: int = 0

    concurrent_tasks: int = 0

    worker_tasks: int = 0
