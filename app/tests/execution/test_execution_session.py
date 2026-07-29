"""
Unit tests for V7.9 ExecutionSession.
"""

from datetime import UTC, datetime

from app.orchestration.execution.execution_context import (
    ExecutionContext,
)
from app.orchestration.execution.execution_session import (
    ExecutionSession,
)


class MockExecutionGraph:
    pass


def test_execution_session_creation():

    graph = MockExecutionGraph()
    context = ExecutionContext()

    session = ExecutionSession(
        execution_graph=graph,
        execution_context=context,
    )

    assert session.execution_graph is graph
    assert session.execution_context is context
    assert session.decision is None


def test_execution_session_accepts_decision():

    graph = MockExecutionGraph()
    context = ExecutionContext()

    decision = object()

    session = ExecutionSession(
        execution_graph=graph,
        execution_context=context,
        decision=decision,
    )

    assert session.decision is decision


def test_execution_session_creates_timestamp():

    session = ExecutionSession(
        execution_graph=MockExecutionGraph(),
        execution_context=ExecutionContext(),
    )

    assert isinstance(
        session.created_at,
        datetime,
    )


def test_execution_session_timestamp_is_timezone_aware():

    session = ExecutionSession(
        execution_graph=MockExecutionGraph(),
        execution_context=ExecutionContext(),
    )

    assert session.created_at.tzinfo == UTC
