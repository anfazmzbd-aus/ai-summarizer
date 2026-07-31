"""
Architecture tests for runtime object ownership.

These tests protect the intended runtime layering:

RuntimeManager
    ↓
RuntimeSession
    ↓
RuntimeContext
    ↓
RuntimeMetadata
"""

from unittest.mock import Mock

from app.runtime.runtime_manager import RuntimeManager
from app.runtime.runtime_session import RuntimeSession


def test_runtime_session_owns_runtime_context() -> None:
    session = RuntimeSession()

    assert session.runtime_context is not None


def test_runtime_context_references_runtime_metadata() -> None:
    session = RuntimeSession()

    assert session.runtime_context.metadata is session.metadata


def test_runtime_context_references_execution_context() -> None:
    session = RuntimeSession()

    assert session.runtime_context.execution_context is session.execution_context


def test_runtime_context_references_runtime_config() -> None:
    session = RuntimeSession()

    assert session.runtime_context.config is session.config


def test_runtime_manager_stores_scheduler_and_execution_engine() -> None:
    scheduler = Mock()
    execution_engine = Mock()

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
    )

    assert manager.scheduler is scheduler
    assert manager.execution_engine is execution_engine
