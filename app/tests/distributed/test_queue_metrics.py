import pytest

from app.distributed.queue.local_queue import (
    LocalExecutionQueue,
)

from app.distributed.protocols import (
    TaskEnvelope,
)

from app.observability.metrics import (
    MetricsRegistry,
    RuntimeMetrics,
)


def create_task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_queue_metrics():

    registry = MetricsRegistry()

    metrics = RuntimeMetrics(registry)

    queue = LocalExecutionQueue(metrics=metrics)

    await queue.enqueue(create_task())

    assert metrics.queue_depth.value == 1

    await queue.dequeue()

    assert metrics.queue_depth.value == 0
