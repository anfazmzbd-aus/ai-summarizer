from app.runtime.runtime_session import RuntimeSession


def test_runtime_session_initializes_components() -> None:
    session = RuntimeSession()

    assert session.runtime_context is not None
    assert session.execution_context is not None
    assert session.config is not None
    assert session.metadata is not None
    assert session.cancellation_token is not None


def test_runtime_context_references_session_objects() -> None:
    session = RuntimeSession()

    assert session.runtime_context.execution_context is session.execution_context

    assert session.runtime_context.metadata is session.metadata

    assert session.runtime_context.config is session.config

    assert session.runtime_context.cancellation_token is session.cancellation_token
