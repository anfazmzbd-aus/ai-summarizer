"""
AI Summarizer V8.0 Distributed Runtime

Worker registry.
"""

from __future__ import annotations

from app.distributed.workers.worker_spec import (
    WorkerSpec,
    WorkerStatus,
)


class WorkerRegistry:
    """
    Maintains active workers.
    """

    def __init__(self) -> None:

        self._workers: dict[str, WorkerSpec] = {}

    def register(
        self,
        worker: WorkerSpec,
    ) -> None:

        self._workers[worker.worker_id] = worker

    def remove(
        self,
        worker_id: str,
    ) -> None:

        self._workers.pop(
            worker_id,
            None,
        )

    def get(
        self,
        worker_id: str,
    ) -> WorkerSpec | None:

        return self._workers.get(worker_id)

    def list_workers(
        self,
    ) -> list[WorkerSpec]:

        return list(self._workers.values())

    def ready_workers(
        self,
    ) -> list[WorkerSpec]:

        return [
            worker
            for worker in self._workers.values()
            if worker.status == WorkerStatus.READY
        ]

    def count(
        self,
    ) -> int:

        return len(self._workers)
