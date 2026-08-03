import pytest

from app.distributed.workers.worker import Worker
from app.distributed.workers.worker_spec import WorkerSpec

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


class FakeExecutor:

    async def execute(
        self,
        task,
    ):
        return "ok"


def create_task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


@pytest.mark.anyio
async def test_worker_metrics():

    registry = MetricsRegistry()

    metrics = RuntimeMetrics(registry)

    worker = Worker(
        spec=WorkerSpec(
            worker_id="worker-1",
            hostname="localhost",
        ),
        queue=LocalExecutionQueue(),
        executor=FakeExecutor(),
        metrics=metrics,
    )

    worker._running = True

    await worker.execute_task(create_task())

    assert metrics.tasks_completed.value == 1

    assert metrics.execution_latency.count == 1
