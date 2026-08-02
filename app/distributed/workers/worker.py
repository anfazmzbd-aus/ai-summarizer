"""
AI Summarizer V8.0 Distributed Runtime

Production worker runtime.
"""

from __future__ import annotations

import asyncio

# from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import (
    ExecutionQueue,
    QueueEmptyError,
)

from .heartbeat import Heartbeat
from .worker_metrics import WorkerMetrics
from .worker_spec import (
    WorkerSpec,
    WorkerStatus,
)


class Worker:
    """
    Production distributed worker.
    """

    def __init__(
        self,
        spec: WorkerSpec,
        queue: ExecutionQueue,
        executor: Any,
    ) -> None:

        self.spec = spec

        self.queue = queue

        self.executor = executor

        self.metrics = WorkerMetrics()

        self._running = False

        self._shutdown = asyncio.Event()

    @property
    def running(self) -> bool:

        return self._running

    async def start(self) -> None:

        if self._running:
            return

        self._running = True

        self.spec.status = WorkerStatus.READY

        while not self._shutdown.is_set():

            try:

                task = await asyncio.wait_for(
                    self.queue.dequeue(),
                    timeout=1.0,
                )

            except TimeoutError:
                continue

            except QueueEmptyError:
                break

            except asyncio.CancelledError:
                break

            await self.execute_task(task)

            if hasattr(
                self.queue,
                "task_done",
            ):
                self.queue.task_done()

        self._running = False

        self.spec.status = WorkerStatus.OFFLINE

    async def stop(self) -> None:

        self._shutdown.set()

    async def execute_task(
        self,
        task: TaskEnvelope,
    ) -> None:

        start = datetime.now(timezone.utc)

        self.metrics.record_received()

        self.metrics.start_task()

        self.spec.status = WorkerStatus.BUSY

        try:

            await self.executor.execute(task)

            elapsed = (datetime.now(timezone.utc) - start).total_seconds()

            self.metrics.record_completed(elapsed)

        except asyncio.CancelledError:

            raise

        except Exception:

            self.metrics.record_failed()

            raise

        finally:

            self.spec.active_tasks = self.metrics.active_tasks

            if self._running:

                self.spec.status = WorkerStatus.READY

    async def wait_closed(self) -> None:

        while self._running:

            await asyncio.sleep(0.05)

    def heartbeat(self) -> Heartbeat:

        return Heartbeat.create(
            worker_id=self.spec.worker_id,
            active_tasks=self.metrics.active_tasks,
        )
