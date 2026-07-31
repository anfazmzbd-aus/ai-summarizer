"""
AI Summarizer V8.0 Distributed Runtime

Distributed worker execution unit.
"""

from __future__ import annotations

# import asyncio
from datetime import datetime, timezone

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import ExecutionQueue

from .heartbeat import Heartbeat
from .worker_metrics import WorkerMetrics
from .worker_spec import WorkerSpec, WorkerStatus


class Worker:
    """
    Executes queued tasks.

    The worker delegates actual execution
    to the V7.9 execution runtime.
    """

    def __init__(
        self,
        spec: WorkerSpec,
        queue: ExecutionQueue,
        executor,
    ) -> None:

        self.spec = spec

        self.queue = queue

        self.executor = executor

        self.metrics = WorkerMetrics()

        self.running = False

    async def start(
        self,
    ) -> None:

        self.running = True

        self.spec.status = WorkerStatus.READY

        while self.running:

            task = await self.queue.dequeue()

            await self.execute_task(task)

    async def stop(
        self,
    ) -> None:

        self.running = False

        self.spec.status = WorkerStatus.OFFLINE

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

            duration = (datetime.now(timezone.utc) - start).total_seconds()

            self.metrics.record_completed(duration)

        except Exception:

            self.metrics.record_failed()

            raise

        finally:

            self.spec.active_tasks = self.metrics.active_tasks

            self.spec.status = WorkerStatus.READY

    def heartbeat(
        self,
    ) -> Heartbeat:

        return Heartbeat.create(
            worker_id=self.spec.worker_id,
            active_tasks=self.metrics.active_tasks,
        )
