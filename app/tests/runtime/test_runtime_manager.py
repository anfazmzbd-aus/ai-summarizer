from unittest.mock import Mock

from app.runtime.runtime_manager import RuntimeManager


def test_runtime_manager_stores_execution_engine() -> None:
    engine = Mock()

    manager = RuntimeManager(engine)

    assert manager.execution_engine is engine
