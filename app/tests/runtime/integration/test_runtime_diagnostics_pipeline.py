from app.runtime.runtime_session import (
    RuntimeSession,
)


def test_runtime_session_creates_diagnostics():

    session = RuntimeSession()

    assert session.diagnostics is not None

    assert session.diagnostics.healthy is True


def test_runtime_context_exposes_diagnostics():

    session = RuntimeSession()

    assert session.runtime_context.diagnostics is session.diagnostics


def test_runtime_metadata_receives_diagnostics():

    session = RuntimeSession()

    session.metadata.diagnostics = session.diagnostics

    assert session.metadata.diagnostics is session.diagnostics
