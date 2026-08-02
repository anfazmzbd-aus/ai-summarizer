import pytest

from app.distributed.coordinator import (
    ResultCollector,
    RuntimeCoordinator,
    TaskDispatcher,
)
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
        return


@pytest.mark.anyio
async def test_runtime_shutdown():

    queue = LocalExecutionQueue()

    manager = WorkerManager()

    manager.add_worker(
        Worker(
            WorkerSpec(
                worker_id="worker-001",
                hostname="localhost",
            ),
            queue,
            FakeExecutor(),
        )
    )

    runtime = RuntimeCoordinator(
        TaskDispatcher(queue),
        ResultCollector(),
        manager,
    )

    await runtime.start()

    await runtime.stop()

    assert manager.count() == 1
