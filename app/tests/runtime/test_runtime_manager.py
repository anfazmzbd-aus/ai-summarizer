from unittest.mock import Mock

from app.runtime.runtime_manager import RuntimeManager


def test_runtime_manager_stores_dependencies() -> None:
    scheduler = Mock()
    engine = Mock()

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=engine,
    )

    assert manager.scheduler is scheduler
    assert manager.execution_engine is engine


def test_runtime_manager_accepts_decision_engine() -> None:
    scheduler = Mock()
    engine = Mock()
    decision_engine = Mock()

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=engine,
        decision_engine=decision_engine,
    )

    assert manager._decision_engine is decision_engine
