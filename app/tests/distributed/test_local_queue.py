import asyncio

import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import (
    LocalExecutionQueue,
    QueueError,
)


def create_task(task_id: str = "task-001") -> TaskEnvelope:

    return TaskEnvelope(
        task_id=task_id,
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_enqueue_dequeue():

    queue = LocalExecutionQueue()

    task = create_task()

    await queue.enqueue(task)

    result = await queue.dequeue()

    assert result.task_id == task.task_id

    queue.task_done()


@pytest.mark.anyio
async def test_join():

    queue = LocalExecutionQueue()

    await queue.enqueue(create_task())

    task = await queue.dequeue()

    queue.task_done()

    await queue.join()

    assert task.task_id == "task-001"


@pytest.mark.anyio
async def test_close():

    queue = LocalExecutionQueue()

    queue.close()

    assert queue.closed


@pytest.mark.anyio
async def test_enqueue_closed_queue():

    queue = LocalExecutionQueue()

    queue.close()

    with pytest.raises(QueueError):

        await queue.enqueue(create_task())


@pytest.mark.anyio
async def test_clear():

    queue = LocalExecutionQueue()

    for i in range(5):

        await queue.enqueue(create_task(str(i)))

    await queue.clear()

    assert queue.empty()


@pytest.mark.anyio
async def test_blocking_dequeue():

    queue = LocalExecutionQueue()

    async def producer():

        await asyncio.sleep(0.01)

        await queue.enqueue(create_task())

    producer_task = asyncio.create_task(producer())

    task = await queue.dequeue()

    assert task.task_id == "task-001"

    queue.task_done()

    await producer_task
