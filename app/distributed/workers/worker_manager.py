"""
AI Summarizer V8.0 Distributed Runtime

Production worker manager.
"""

from __future__ import annotations

import asyncio
from contextlib import suppress

from .worker import Worker


class WorkerManager:
    """
    Supervises worker lifecycle.
    """

    def __init__(self) -> None:

        self._workers: dict[str, Worker] = {}

        self._tasks: dict[str, asyncio.Task[None]] = {}

    def add_worker(
        self,
        worker: Worker,
    ) -> None:

        worker_id = worker.spec.worker_id

        if worker_id in self._workers:
            raise ValueError(f"Worker '{worker_id}' already registered.")

        self._workers[worker_id] = worker

    def get_worker(
        self,
        worker_id: str,
    ) -> Worker | None:

        return self._workers.get(worker_id)

    def workers(
        self,
    ) -> list[Worker]:

        return list(self._workers.values())

    def count(
        self,
    ) -> int:

        return len(self._workers)

    async def start_worker(
        self,
        worker_id: str,
    ) -> None:

        worker = self._workers[worker_id]

        if worker_id in self._tasks:

            task = self._tasks[worker_id]

            if not task.done():
                return

        task = asyncio.create_task(
            worker.start(),
            name=f"worker:{worker_id}",
        )

        self._tasks[worker_id] = task

        await asyncio.sleep(0)

    async def start_all(
        self,
    ) -> None:

        for worker_id in self._workers:
            await self.start_worker(worker_id)

    async def stop_worker(
        self,
        worker_id: str,
    ) -> None:

        worker = self._workers[worker_id]

        await worker.stop()

        task = self._tasks.get(worker_id)

        if task is None:
            return

        with suppress(asyncio.CancelledError):
            await asyncio.wait_for(
                task,
                timeout=2.0,
            )

        self._tasks.pop(worker_id, None)

    async def stop_all(
        self,
    ) -> None:

        for worker_id in list(self._workers):
            await self.stop_worker(worker_id)

    async def wait_all(
        self,
    ) -> None:

        if not self._tasks:
            return

        await asyncio.gather(
            *self._tasks.values(),
            return_exceptions=True,
        )
