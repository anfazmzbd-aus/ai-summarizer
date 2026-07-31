import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.coordinator import (
    RuntimeCoordinator,
    ResultCollector,
    TaskDispatcher,
    ExecutionResult,
)


def create_task():

    return TaskEnvelope(
        task_id="task-001",
        execution_id="exec-001",
        node_id="node-001",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_submit_task():

    queue = LocalExecutionQueue()

    coordinator = RuntimeCoordinator(
        TaskDispatcher(queue),
        ResultCollector(),
    )

    await coordinator.submit(create_task())

    assert queue.size() == 1


def test_record_result():

    coordinator = RuntimeCoordinator(
        TaskDispatcher(LocalExecutionQueue()),
        ResultCollector(),
    )

    coordinator.record_result(
        ExecutionResult(
            task_id="task-001",
            success=True,
        )
    )

    assert coordinator.get_result("task-001").success is True
