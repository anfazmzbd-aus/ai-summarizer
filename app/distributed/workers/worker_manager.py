"""
AI Summarizer V8.0 Distributed Runtime

Worker lifecycle manager.
"""

from __future__ import annotations

import asyncio

from .worker import Worker


class WorkerManager:
    """
    Controls worker lifecycle.
    """

    def __init__(self) -> None:

        self._workers: dict[str, Worker] = {}

        self._tasks: dict[str, asyncio.Task] = {}

    def add_worker(
        self,
        worker: Worker,
    ) -> None:

        self._workers[worker.spec.worker_id] = worker

    async def start_worker(
        self,
        worker_id: str,
    ) -> None:

        worker = self._workers[worker_id]

        task = asyncio.create_task(worker.start())

        self._tasks[worker_id] = task

    async def stop_worker(
        self,
        worker_id: str,
    ) -> None:

        worker = self._workers[worker_id]

        await worker.stop()

        task = self._tasks.get(worker_id)

        if task:

            task.cancel()

    async def stop_all(
        self,
    ) -> None:

        for worker_id in list(self._workers):

            await self.stop_worker(worker_id)

    def get_worker(
        self,
        worker_id: str,
    ) -> Worker | None:

        return self._workers.get(worker_id)

    def count(
        self,
    ) -> int:

        return len(self._workers)
