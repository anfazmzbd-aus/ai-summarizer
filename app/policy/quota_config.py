"""
Quota policy configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class QuotaConfig:

    max_queue_depth: int = 1000

    max_concurrent_tasks: int = 100

    max_worker_tasks: int = 10
