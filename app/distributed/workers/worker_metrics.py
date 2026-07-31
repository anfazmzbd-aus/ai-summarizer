"""
AI Summarizer V8.0 Distributed Runtime

Worker execution metrics.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class WorkerMetrics:
    """
    Runtime statistics for a worker.
    """

    tasks_received: int = 0

    tasks_completed: int = 0

    tasks_failed: int = 0

    retry_count: int = 0

    active_tasks: int = 0

    total_execution_time: float = 0.0

    def record_received(self) -> None:
        self.tasks_received += 1

    def record_completed(
        self,
        execution_time: float,
    ) -> None:

        self.tasks_completed += 1

        self.active_tasks -= 1

        self.total_execution_time += execution_time

    def record_failed(self) -> None:

        self.tasks_failed += 1

        self.active_tasks -= 1

    def start_task(self) -> None:

        self.active_tasks += 1
