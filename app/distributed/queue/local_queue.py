"""
AI Summarizer V8.0 Distributed Runtime

Local asynchronous execution queue.
"""

from __future__ import annotations

import asyncio

from app.distributed.protocols import TaskEnvelope

from .exceptions import QueueEmptyError, QueueFullError
from .queue_interface import ExecutionQueue


class LocalExecutionQueue(ExecutionQueue):
    """
    In-memory async execution queue.

    Used for:
    - Development
    - Testing
    - Single-node execution
    """

    def __init__(
        self,
        max_size: int = 0,
    ) -> None:

        self._queue: asyncio.Queue[TaskEnvelope] = asyncio.Queue(maxsize=max_size)

    async def enqueue(
        self,
        task: TaskEnvelope,
    ) -> None:

        try:
            self._queue.put_nowait(task)

        except asyncio.QueueFull as exc:
            raise QueueFullError("Execution queue is full") from exc

    async def dequeue(
        self,
    ) -> TaskEnvelope:

        try:
            return self._queue.get_nowait()

        except asyncio.QueueEmpty as exc:
            raise QueueEmptyError("Execution queue is empty") from exc

    def size(self) -> int:

        return self._queue.qsize()

    def empty(self) -> bool:

        return self._queue.empty()

    async def clear(self) -> None:

        while not self._queue.empty():

            try:
                self._queue.get_nowait()

            except asyncio.QueueEmpty:
                break
