from app.runtime.observability.execution_metrics import (
    ExecutionMetrics,
)
from app.runtime.observability.execution_timeline import (
    ExecutionTimeline,
)
from app.runtime.observability.runtime_snapshot import (
    RuntimeSnapshot,
)


def test_runtime_snapshot_defaults():
    snapshot = RuntimeSnapshot(
        metrics=ExecutionMetrics(),
        timeline=ExecutionTimeline(),
    )

    assert snapshot.strategy is None

    assert snapshot.metrics.total_layers == 0

    assert snapshot.timeline.events == []
