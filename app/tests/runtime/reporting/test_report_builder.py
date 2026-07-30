from app.runtime.diagnostics.runtime_diagnostics import (
    RuntimeDiagnostics,
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

from app.runtime.reporting.report_builder import (
    ReportBuilder,
)


def create_snapshot():

    return RuntimeSnapshot(
        metrics=ExecutionMetrics(
            total_layers=4,
            completed_layers=4,
            failed_nodes=0,
            execution_time_seconds=2.5,
        ),
        timeline=ExecutionTimeline(),
    )


def test_report_builder_creates_report():

    builder = ReportBuilder()

    diagnostics = RuntimeDiagnostics()

    report = builder.build_report(
        create_snapshot(),
        diagnostics,
    )

    assert report.status == "healthy"

    assert report.healthy is True

    assert report.total_layers == 4

    assert report.completed_layers == 4


def test_report_builder_creates_summary():

    builder = ReportBuilder()

    diagnostics = RuntimeDiagnostics()

    summary = builder.build_summary(
        create_snapshot(),
        diagnostics,
    )

    assert summary.status == "healthy"

    assert summary.completion_rate == 1.0

    assert summary.execution_time_seconds == 2.5


def test_report_builder_handles_failure():

    builder = ReportBuilder()

    diagnostics = RuntimeDiagnostics(
        healthy=False,
        issues=["Node execution failed"],
    )

    report = builder.build_report(
        create_snapshot(),
        diagnostics,
    )

    assert report.status == "failed"

    assert report.healthy is False

    assert report.issues == ["Node execution failed"]
