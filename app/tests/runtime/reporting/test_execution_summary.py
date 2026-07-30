from app.runtime.reporting.execution_summary import (
    ExecutionSummary,
)


def test_execution_summary_creation():

    summary = ExecutionSummary(
        status="healthy",
        completion_rate=1.0,
        execution_time_seconds=2.5,
        healthy=True,
    )

    assert summary.status == "healthy"
    assert summary.completion_rate == 1.0
    assert summary.execution_time_seconds == 2.5
    assert summary.healthy is True
