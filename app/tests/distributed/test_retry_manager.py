import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.recovery import (
    DeadLetterQueue,
    RetryManager,
    RetryPolicy,
)


def create_task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_retry_success():

    queue = LocalExecutionQueue()

    manager = RetryManager(
        queue=queue,
        policy=RetryPolicy(
            max_attempts=3,
            backoff_seconds=0,
        ),
        dead_letter_queue=DeadLetterQueue(),
    )

    task = create_task()

    result = await manager.handle_failure(task)

    assert result

    assert queue.size() == 1

    assert task.retry_count == 1


@pytest.mark.anyio
async def test_dead_letter():

    queue = LocalExecutionQueue()

    dlq = DeadLetterQueue()

    manager = RetryManager(
        queue=queue,
        policy=RetryPolicy(
            max_attempts=1,
            backoff_seconds=0,
        ),
        dead_letter_queue=dlq,
    )

    task = create_task()

    task.increment_retry()

    result = await manager.handle_failure(task)

    assert result is False

    assert dlq.size() == 1
