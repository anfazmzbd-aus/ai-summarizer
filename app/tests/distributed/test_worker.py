import asyncio

import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.workers import Worker
from app.distributed.workers.worker_spec import WorkerSpec


class FakeExecutor:

    def __init__(self):

        self.executed = []

    async def execute(self, task):

        self.executed.append(task)


def create_worker():

    return Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        LocalExecutionQueue(),
        FakeExecutor(),
    )


def create_task():

    return TaskEnvelope(
        task_id="task-001",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_execute_task():

    worker = create_worker()

    await worker.execute_task(create_task())

    assert worker.metrics.tasks_completed == 1


@pytest.mark.anyio
async def test_worker_start_stop():

    worker = create_worker()

    task = asyncio.create_task(worker.start())

    await asyncio.sleep(0.05)

    assert worker.running

    await worker.stop()

    await task

    assert not worker.running


@pytest.mark.anyio
async def test_worker_process_queue():

    worker = create_worker()

    await worker.queue.enqueue(create_task())

    runtime = asyncio.create_task(worker.start())

    await asyncio.sleep(0.2)

    await worker.stop()

    await runtime

    assert worker.metrics.tasks_completed == 1


@pytest.mark.anyio
async def test_heartbeat():

    worker = create_worker()

    heartbeat = worker.heartbeat()

    assert heartbeat.worker_id == "worker-001"
