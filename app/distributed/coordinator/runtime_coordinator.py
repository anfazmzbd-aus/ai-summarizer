"""
AI Summarizer V8.0 Distributed Runtime

Distributed runtime coordinator.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope

from .result_collector import (
    ResultCollector,
    ExecutionResult,
)

from .task_dispatcher import TaskDispatcher


class RuntimeCoordinator:
    """
    Coordinates distributed execution.
    """

    def __init__(
        self,
        dispatcher: TaskDispatcher,
        collector: ResultCollector,
    ) -> None:

        self.dispatcher = dispatcher

        self.collector = collector

    async def submit(
        self,
        task: TaskEnvelope,
    ) -> None:

        await self.dispatcher.dispatch(task)

    def record_result(
        self,
        result: ExecutionResult,
    ) -> None:

        self.collector.add(result)

    def get_result(
        self,
        task_id: str,
    ) -> ExecutionResult | None:

        return self.collector.get(task_id)
