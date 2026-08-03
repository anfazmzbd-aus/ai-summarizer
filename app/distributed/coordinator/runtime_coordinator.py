"""
AI Summarizer V8.0

Production Runtime Coordinator.
"""

from __future__ import annotations

# import asyncio

from app.distributed.protocols import TaskEnvelope
from app.distributed.workers import WorkerManager

from .result_collector import (
    ExecutionResult,
    ResultCollector,
)
from .task_dispatcher import TaskDispatcher
from app.observability.metrics import RuntimeMetrics


class RuntimeCoordinator:
    """
    Coordinates distributed execution.

    Responsibilities
    ----------------
    - Submit work
    - Start workers
    - Wait for completion
    - Aggregate results
    - Graceful shutdown
    """

    def __init__(
        self,
        dispatcher: TaskDispatcher,
        collector: ResultCollector,
        worker_manager: WorkerManager,
        metrics: RuntimeMetrics | None = None,
    ) -> None:

        self._dispatcher = dispatcher
        self._collector = collector
        self._worker_manager = worker_manager
        self._metrics = metrics
        self._started = False

    async def start(self) -> None:

        if self._started:
            return

        await self._worker_manager.start_all()

        self._started = True

    async def stop(self) -> None:

        if not self._started:
            return

        await self._worker_manager.stop_all()

        self._started = False

    async def submit(
        self,
        task: TaskEnvelope,
    ) -> None:

        if self._metrics:

            self._metrics.task_submitted()

        await self._dispatcher.dispatch(task)

    async def submit_many(
        self,
        tasks: list[TaskEnvelope],
    ) -> None:

        await self._dispatcher.dispatch_many(tasks)

    async def wait_for_completion(self) -> None:

        for worker in self._worker_manager.workers():

            queue = worker.queue

            if hasattr(queue, "join"):
                await queue.join()

    def record_result(
        self,
        result: ExecutionResult,
    ) -> None:

        self._collector.add(result)

    def get_result(
        self,
        task_id: str,
    ) -> ExecutionResult | None:

        return self._collector.get(task_id)

    def results(
        self,
    ) -> list[ExecutionResult]:

        return self._collector.all()
