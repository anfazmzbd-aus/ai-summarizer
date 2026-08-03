import pytest

from app.distributed.queue.local_queue import (
    LocalExecutionQueue,
)

from app.distributed.recovery.dead_letter_queue import (
    DeadLetterQueue,
)

from app.distributed.recovery.retry_manager import (
    RetryManager,
)

from app.distributed.recovery.retry_policy import (
    RetryPolicy,
)

from app.distributed.protocols import (
    TaskEnvelope,
)

from app.observability.metrics import (
    MetricsRegistry,
    RuntimeMetrics,
)


@pytest.mark.anyio
async def test_retry_counter():

    registry = MetricsRegistry()

    metrics = RuntimeMetrics(registry)

    manager = RetryManager(
        queue=LocalExecutionQueue(),
        policy=RetryPolicy(
            max_attempts=2,
            backoff_seconds=0,
        ),
        dead_letter_queue=DeadLetterQueue(),
        metrics=metrics,
    )

    task = TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )

    await manager.handle_failure(task)

    assert metrics.retries.value == 1
