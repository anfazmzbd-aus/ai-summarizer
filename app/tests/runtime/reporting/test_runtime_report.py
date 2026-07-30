from app.runtime.reporting.runtime_report import RuntimeReport


def test_runtime_report_defaults():

    report = RuntimeReport(
        status="healthy",
        execution_time_seconds=1.5,
        total_layers=2,
        completed_layers=2,
        failed_nodes=0,
        healthy=True,
    )

    assert report.status == "healthy"
    assert report.execution_time_seconds == 1.5
    assert report.total_layers == 2
    assert report.completed_layers == 2
    assert report.failed_nodes == 0
    assert report.healthy is True
    assert report.issues == []
    assert report.warnings == []


def test_runtime_report_with_issues():

    report = RuntimeReport(
        status="failed",
        execution_time_seconds=3.0,
        total_layers=3,
        completed_layers=2,
        failed_nodes=1,
        healthy=False,
        issues=["Execution contains failed nodes."],
    )

    assert report.healthy is False
    assert report.failed_nodes == 1
    assert len(report.issues) == 1
