"""
Current runtime resource state.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ResourceState:

    cpu_percent: float = 0.0

    memory_percent: float = 0.0

    queue_pressure: float = 0.0

    worker_utilization: float = 0.0
