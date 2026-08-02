import asyncio

import pytest

from app.distributed.queue import LocalExecutionQueue
from app.distributed.workers import Worker
from app.distributed.workers.worker_spec import WorkerSpec


class SlowExecutor:

    async def execute(
        self,
        task,
    ) -> None:

        await asyncio.sleep(0.2)


@pytest.mark.anyio
async def test_graceful_shutdown():

    worker = Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        LocalExecutionQueue(),
        SlowExecutor(),
    )

    runtime = asyncio.create_task(worker.start())

    await asyncio.sleep(0.05)

    await worker.stop()

    await runtime

    assert worker.running is False
