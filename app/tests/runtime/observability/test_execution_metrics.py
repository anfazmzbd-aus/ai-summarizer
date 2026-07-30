from app.runtime.observability.execution_metrics import ExecutionMetrics


def test_execution_metrics_defaults():
    metrics = ExecutionMetrics()

    assert metrics.total_layers == 0
    assert metrics.completed_layers == 0
    assert metrics.total_nodes == 0
    assert metrics.completed_nodes == 0
    assert metrics.execution_time_seconds == 0.0
    assert metrics.parallel_layers == 0
    assert metrics.failed_nodes == 0
    assert metrics.retried_nodes == 0
    assert metrics.cache_hits == 0
    assert metrics.cache_misses == 0
    assert metrics.custom == {}


def test_execution_metrics_mutable():
    metrics = ExecutionMetrics()

    metrics.total_layers = 5
    metrics.completed_layers = 3
    metrics.custom["runtime"] = "production"

    assert metrics.total_layers == 5
    assert metrics.completed_layers == 3
    assert metrics.custom["runtime"] == "production"
