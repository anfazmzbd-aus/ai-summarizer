from app.distributed.protocols import TaskEnvelope
from app.distributed.recovery import (
    DeadLetterQueue,
    FailureHandler,
    RetryPolicy,
)


def create_task():

    return TaskEnvelope(
        task_id="1",
        execution_id="e",
        node_id="n",
        agent_type="summary",
    )


def test_retry():

    handler = FailureHandler(
        RetryPolicy(max_attempts=3),
        DeadLetterQueue(),
    )

    assert handler.process_failure(create_task())


def test_dead_letter():

    dlq = DeadLetterQueue()

    handler = FailureHandler(
        RetryPolicy(max_attempts=1),
        dlq,
    )

    task = create_task()

    assert not handler.process_failure(task)

    assert dlq.size() == 1
