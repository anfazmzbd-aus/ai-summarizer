from app.runtime.diagnostics.execution_statistics import (
    ExecutionStatistics,
)

from app.runtime.observability.execution_metrics import (
    ExecutionMetrics,
)

from app.runtime.observability.execution_timeline import (
    ExecutionTimeline,
)

from app.runtime.observability.runtime_snapshot import (
    RuntimeSnapshot,
)


def test_execution_statistics_calculation():

    snapshot = RuntimeSnapshot(
        metrics=ExecutionMetrics(
            total_layers=4,
            completed_layers=4,
            failed_nodes=0,
            execution_time_seconds=2.5,
        ),
        timeline=ExecutionTimeline(),
    )

    statistics = ExecutionStatistics()

    result = statistics.calculate(
        snapshot,
    )

    assert result["total_layers"] == 4

    assert result["completed_layers"] == 4

    assert result["completion_rate"] == 1.0

    assert result["execution_time_seconds"] == 2.5


def test_execution_statistics_zero_layers():

    snapshot = RuntimeSnapshot(
        metrics=ExecutionMetrics(),
        timeline=ExecutionTimeline(),
    )

    statistics = ExecutionStatistics()

    result = statistics.calculate(
        snapshot,
    )

    assert result["completion_rate"] == 0.0
