import pytest
import asyncio
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
    ):

        return None


def create_worker():

    return Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        LocalExecutionQueue(),
        FakeExecutor(),
    )


def test_add_worker():

    manager = WorkerManager()

    worker = create_worker()

    manager.add_worker(worker)

    assert manager.count() == 1


def test_get_worker():

    manager = WorkerManager()

    worker = create_worker()

    manager.add_worker(worker)

    result = manager.get_worker("worker-001")

    assert result == worker


@pytest.mark.anyio
async def test_start_and_stop_worker():

    manager = WorkerManager()

    worker = create_worker()

    manager.add_worker(worker)

    await manager.start_worker("worker-001")

    await asyncio.sleep(0)

    assert worker.running is True

    await manager.stop_worker("worker-001")

    assert worker.running is False


@pytest.mark.anyio
async def test_stop_all_workers():

    manager = WorkerManager()

    worker = create_worker()

    manager.add_worker(worker)

    await manager.start_worker("worker-001")

    await manager.stop_all()

    assert worker.running is False
