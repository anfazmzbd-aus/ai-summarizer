from __future__ import annotations

from app.runtime.observability.runtime_snapshot import (
    RuntimeSnapshot,
)


class ExecutionStatistics:
    """
    Calculates runtime execution statistics.
    """

    def calculate(
        self,
        snapshot: RuntimeSnapshot,
    ) -> dict[str, object]:

        metrics = snapshot.metrics

        completion_rate = 0.0

        if metrics.total_layers:
            completion_rate = metrics.completed_layers / metrics.total_layers

        return {
            "total_layers": metrics.total_layers,
            "completed_layers": metrics.completed_layers,
            "completion_rate": completion_rate,
            "failed_nodes": metrics.failed_nodes,
            "execution_time_seconds": (metrics.execution_time_seconds),
        }
