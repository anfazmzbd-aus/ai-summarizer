from app.observability.metrics import (
    MetricsRegistry,
    RuntimeMetrics,
)


def test_runtime_metrics():

    registry = MetricsRegistry()

    metrics = RuntimeMetrics(registry)

    metrics.task_submitted()

    metrics.task_completed(15)

    metrics.retry()

    metrics.dead_letter()

    metrics.set_queue_depth(7)

    metrics.set_active_workers(3)

    assert metrics.tasks_submitted.value == 1

    assert metrics.tasks_completed.value == 1

    assert metrics.execution_latency.count == 1

    assert metrics.queue_depth.value == 7
