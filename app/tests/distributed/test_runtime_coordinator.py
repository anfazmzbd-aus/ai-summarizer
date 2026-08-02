import asyncio

import pytest

from app.distributed.coordinator import (
    ExecutionResult,
    ResultCollector,
    RuntimeCoordinator,
    TaskDispatcher,
)
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


def create_task(task_id="1"):

    return TaskEnvelope(
        task_id=task_id,
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


def build_runtime():

    queue = LocalExecutionQueue()

    manager = WorkerManager()

    worker = Worker(
        WorkerSpec(
            worker_id="worker-001",
            hostname="localhost",
        ),
        queue,
        FakeExecutor(),
    )

    manager.add_worker(worker)

    coordinator = RuntimeCoordinator(
        TaskDispatcher(queue),
        ResultCollector(),
        manager,
    )

    return coordinator


@pytest.mark.anyio
async def test_submit():

    coordinator = build_runtime()

    await coordinator.submit(create_task())


@pytest.mark.anyio
async def test_submit_many():

    coordinator = build_runtime()

    await coordinator.submit_many(
        [
            create_task("1"),
            create_task("2"),
            create_task("3"),
        ]
    )


@pytest.mark.anyio
async def test_runtime_start_stop():

    coordinator = build_runtime()

    await coordinator.start()

    await coordinator.stop()


def test_result_collection():

    coordinator = build_runtime()

    coordinator.record_result(
        ExecutionResult(
            task_id="1",
            success=True,
        )
    )

    assert coordinator.get_result("1").success


def test_result_list():

    coordinator = build_runtime()

    coordinator.record_result(
        ExecutionResult(
            task_id="1",
            success=True,
        )
    )

    assert len(coordinator.results()) == 1
