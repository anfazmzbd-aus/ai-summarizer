import asyncio

import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.workers import (
    Worker,
    WorkerManager,
)
from app.distributed.workers.worker_spec import WorkerSpec


class FakeExecutor:

    async def execute(
        self,
        task,
    ) -> None:

        await asyncio.sleep(0.01)


def create_worker() -> Worker:

    return Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        LocalExecutionQueue(),
        FakeExecutor(),
    )


def create_task() -> TaskEnvelope:

    return TaskEnvelope(
        task_id="task-001",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


def test_add_worker():

    manager = WorkerManager()

    manager.add_worker(create_worker())

    assert manager.count() == 1


def test_duplicate_worker():

    manager = WorkerManager()

    manager.add_worker(create_worker())

    with pytest.raises(ValueError):

        manager.add_worker(create_worker())


@pytest.mark.anyio
async def test_start_worker():

    manager = WorkerManager()

    worker = create_worker()

    manager.add_worker(worker)

    await manager.start_worker(worker.spec.worker_id)

    assert worker.running


@pytest.mark.anyio
async def test_stop_worker():

    manager = WorkerManager()

    worker = create_worker()

    manager.add_worker(worker)

    await manager.start_worker(worker.spec.worker_id)

    await manager.stop_worker(worker.spec.worker_id)

    assert not worker.running


@pytest.mark.anyio
async def test_start_all_stop_all():

    manager = WorkerManager()

    manager.add_worker(create_worker())

    await manager.start_all()

    assert manager.count() == 1

    await manager.stop_all()

    assert not manager.get_worker("worker-001").running
