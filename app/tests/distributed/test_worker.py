import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.workers import Worker
from app.distributed.workers.worker_spec import WorkerSpec


class FakeExecutor:

    def __init__(self):

        self.executed = []

    async def execute(
        self,
        task,
    ):

        self.executed.append(task)


def create_task():

    return TaskEnvelope(
        task_id="task-001",
        execution_id="exec-001",
        node_id="node-001",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_worker_execute_task():

    queue = LocalExecutionQueue()

    executor = FakeExecutor()

    worker = Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        queue,
        executor,
    )

    await worker.execute_task(create_task())

    assert len(executor.executed) == 1


@pytest.mark.anyio
async def test_worker_status_after_task():

    queue = LocalExecutionQueue()

    executor = FakeExecutor()

    worker = Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        queue,
        executor,
    )

    await worker.execute_task(create_task())

    assert worker.spec.status.value == "ready"
