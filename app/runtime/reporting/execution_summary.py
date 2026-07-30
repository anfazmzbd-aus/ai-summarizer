from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionSummary:
    """
    Lightweight execution summary.
    """

    status: str

    completion_rate: float

    execution_time_seconds: float

    healthy: bool
