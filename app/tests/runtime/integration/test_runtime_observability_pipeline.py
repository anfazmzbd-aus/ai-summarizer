from app.runtime.runtime_session import RuntimeSession


def test_runtime_session_creates_snapshot():
    session = RuntimeSession()

    assert session.snapshot is not None

    assert session.snapshot.metrics.total_layers == 0

    assert session.snapshot.timeline.events == []


def test_runtime_context_exposes_metrics():
    session = RuntimeSession()

    assert session.runtime_context.metrics is session.snapshot.metrics


def test_runtime_context_exposes_timeline():
    session = RuntimeSession()

    assert session.runtime_context.timeline is session.snapshot.timeline
