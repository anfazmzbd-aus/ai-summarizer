from pytest import mark

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import (
    LocalExecutionQueue,
    QueueEmptyError,
    QueueFullError,
)


def create_task(
    task_id: str = "task-001",
) -> TaskEnvelope:

    return TaskEnvelope(
        task_id=task_id,
        execution_id="execution-001",
        node_id="node-001",
        agent_type="summary",
    )


@mark.anyio
async def test_enqueue_and_dequeue():

    queue = LocalExecutionQueue()

    task = create_task()

    await queue.enqueue(task)

    result = await queue.dequeue()

    assert result.task_id == task.task_id


@mark.anyio
async def test_fifo_order():

    queue = LocalExecutionQueue()

    await queue.enqueue(create_task("task-1"))

    await queue.enqueue(create_task("task-2"))

    first = await queue.dequeue()
    second = await queue.dequeue()

    assert first.task_id == "task-1"
    assert second.task_id == "task-2"


@mark.anyio
async def test_queue_size():

    queue = LocalExecutionQueue()

    await queue.enqueue(create_task())

    assert queue.size() == 1


@mark.anyio
async def test_empty_queue():

    queue = LocalExecutionQueue()

    assert queue.empty()

    try:
        await queue.dequeue()

    except QueueEmptyError:
        assert True

    else:
        assert False


@mark.anyio
async def test_queue_clear():

    queue = LocalExecutionQueue()

    await queue.enqueue(create_task())

    await queue.clear()

    assert queue.empty()


@mark.anyio
async def test_queue_full():

    queue = LocalExecutionQueue(max_size=1)

    await queue.enqueue(create_task("task-1"))

    try:
        await queue.enqueue(create_task("task-2"))

    except QueueFullError:
        assert True

    else:
        assert False
