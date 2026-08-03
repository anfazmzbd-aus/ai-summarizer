"""
Runtime resource policy configuration.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ResourceConfig:

    max_cpu_percent: float = 90.0

    max_memory_percent: float = 90.0

    max_queue_pressure: float = 0.90

    max_worker_utilization: float = 0.95
