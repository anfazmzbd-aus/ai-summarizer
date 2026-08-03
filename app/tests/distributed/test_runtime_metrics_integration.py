from app.observability.metrics import (
    MetricsRegistry,
    RuntimeMetrics,
)


def test_runtime_metric_defaults():

    registry = MetricsRegistry()

    metrics = RuntimeMetrics(registry)

    assert metrics.tasks_submitted.value == 0

    assert metrics.tasks_completed.value == 0

    assert metrics.tasks_failed.value == 0
