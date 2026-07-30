from app.runtime.diagnostics.execution_analyzer import (
    ExecutionAnalyzer,
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


def test_analyzer_marks_successful_execution():

    snapshot = RuntimeSnapshot(
        metrics=ExecutionMetrics(),
        timeline=ExecutionTimeline(),
    )

    analyzer = ExecutionAnalyzer()

    result = analyzer.analyze(
        snapshot,
    )

    assert result.healthy is True

    assert result.issues == []


def test_analyzer_detects_failed_nodes():

    snapshot = RuntimeSnapshot(
        metrics=ExecutionMetrics(
            failed_nodes=2,
        ),
        timeline=ExecutionTimeline(),
    )

    analyzer = ExecutionAnalyzer()

    result = analyzer.analyze(
        snapshot,
    )

    assert result.healthy is False

    assert "Execution contains failed nodes." in result.issues
