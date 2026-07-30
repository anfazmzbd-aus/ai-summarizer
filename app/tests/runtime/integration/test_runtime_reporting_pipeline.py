from app.runtime.runtime_session import RuntimeSession


def test_runtime_session_initializes_without_report():
    session = RuntimeSession()

    assert session.report is None
    assert session.runtime_context.report is None


def test_runtime_session_builds_report():
    session = RuntimeSession()

    session.build_report()

    session.metadata.report = session.report

    assert session.report is not None
    assert session.runtime_context.report is session.report


def test_runtime_report_reflects_diagnostics():
    session = RuntimeSession()

    session.diagnostics.healthy = False
    session.diagnostics.issues.append("Execution contains failed nodes.")

    session.build_report()
    session.metadata.report = session.report

    report = session.runtime_context.report

    assert report is not None
    assert report.healthy is False
    assert report.issues == ["Execution contains failed nodes."]


def test_runtime_report_contains_metrics():
    session = RuntimeSession()

    session.snapshot.metrics.total_layers = 5
    session.snapshot.metrics.completed_layers = 5
    session.snapshot.metrics.execution_time_seconds = 1.75

    session.build_report()
    session.metadata.report = session.report

    report = session.runtime_context.report

    assert report.total_layers == 5
    assert report.completed_layers == 5
    assert report.execution_time_seconds == 1.75
