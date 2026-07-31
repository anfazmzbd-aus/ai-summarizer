"""
AI Summarizer V8.0 Distributed Runtime

Task dispatcher.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import ExecutionQueue


class TaskDispatcher:
    """
    Sends execution tasks to queue.
    """

    def __init__(
        self,
        queue: ExecutionQueue,
    ) -> None:

        self.queue = queue

    async def dispatch(
        self,
        task: TaskEnvelope,
    ) -> None:

        await self.queue.enqueue(task)

    async def dispatch_many(
        self,
        tasks: list[TaskEnvelope],
    ) -> None:

        for task in tasks:

            await self.dispatch(task)
