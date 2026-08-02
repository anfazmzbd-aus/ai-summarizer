import pytest

from app.distributed.protocols import TaskEnvelope
from app.distributed.queue import LocalExecutionQueue
from app.distributed.recovery import (
    DeadLetterQueue,
    RetryManager,
    RetryPolicy,
)


@pytest.mark.anyio
async def test_multiple_failures():

    queue = LocalExecutionQueue()

    dlq = DeadLetterQueue()

    manager = RetryManager(
        queue=queue,
        policy=RetryPolicy(
            max_attempts=3,
            backoff_seconds=0,
        ),
        dead_letter_queue=dlq,
    )

    task = TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )

    assert await manager.handle_failure(task)
    assert await manager.handle_failure(task)
    assert await manager.handle_failure(task)

    # Fourth failure exceeds retry limit
    assert await manager.handle_failure(task) is False

    assert dlq.size() == 1
