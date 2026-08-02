"""
AI Summarizer V8.0 Distributed Runtime

Production local execution queue.
"""

from __future__ import annotations

import asyncio

from app.distributed.protocols import TaskEnvelope

from .exceptions import (
    QueueEmptyError,
    QueueError,
    QueueFullError,
)
from .queue_interface import ExecutionQueue


class LocalExecutionQueue(ExecutionQueue):
    """
    Production in-memory execution queue.
    """

    def __init__(
        self,
        max_size: int = 0,
    ) -> None:

        self._queue: asyncio.Queue[TaskEnvelope] = asyncio.Queue(maxsize=max_size)

        self._closed = False

    async def enqueue(
        self,
        task: TaskEnvelope,
    ) -> None:

        if self._closed:
            raise QueueError("Queue has been closed.")

        try:
            await self._queue.put(task)

        except asyncio.QueueFull as exc:
            raise QueueFullError("Execution queue is full.") from exc

    async def dequeue(
        self,
    ) -> TaskEnvelope:

        if self._closed and self._queue.empty():
            raise QueueEmptyError("Queue has been closed.")

        try:
            return await self._queue.get()

        except asyncio.CancelledError:
            raise

    def task_done(
        self,
    ) -> None:

        self._queue.task_done()

    async def join(
        self,
    ) -> None:

        await self._queue.join()

    async def clear(
        self,
    ) -> None:

        while not self._queue.empty():

            try:
                self._queue.get_nowait()
                self._queue.task_done()

            except asyncio.QueueEmpty:
                break

    def close(
        self,
    ) -> None:

        self._closed = True

    @property
    def closed(
        self,
    ) -> bool:

        return self._closed

    def size(
        self,
    ) -> int:

        return self._queue.qsize()

    def empty(
        self,
    ) -> bool:

        return self._queue.empty()
