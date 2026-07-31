import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.coordinator import TaskDispatcher


def create_task():

    return TaskEnvelope(
        task_id="task-001",
        execution_id="exec-001",
        node_id="node-001",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_dispatch():

    queue = LocalExecutionQueue()

    dispatcher = TaskDispatcher(queue)

    await dispatcher.dispatch(create_task())

    assert queue.size() == 1


@pytest.mark.anyio
async def test_dispatch_many():

    queue = LocalExecutionQueue()

    dispatcher = TaskDispatcher(queue)

    await dispatcher.dispatch_many(
        [
            create_task(),
            create_task(),
        ]
    )

    assert queue.size() == 2
