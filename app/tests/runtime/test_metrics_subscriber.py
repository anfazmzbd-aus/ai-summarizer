from app.orchestration.observability.metrics import RuntimeMetrics
from app.runtime.events.metrics_subscriber import MetricsSubscriber
from app.runtime.events.event_types import NodeFinished


def test_node_finished_updates_metrics():
    # Use the real data object instead of Mock()
    metrics = RuntimeMetrics()

    # Ensure starting state is 0 (if not handled by __init__)
    metrics.node_count = 0

    subscriber = MetricsSubscriber(metrics)

    event = NodeFinished(
        execution_id="exec-001",
        node="summary",
    )

    subscriber(event)

    assert metrics.node_count == 1
