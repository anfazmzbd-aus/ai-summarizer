from unittest.mock import Mock

from app.orchestration.execution.execution_engine import ExecutionEngine


def test_execution_engine_emits_execution_events():

    registry = Mock()
    contracts = Mock()

    # bus = Mock()

    graph = Mock()
    graph.layers = []

    state = Mock()

    publisher = Mock()

    engine = ExecutionEngine(
        registry,
        contracts,
        publisher,
    )

    engine.execute(
        graph,
        state,
    )

    publisher.execution_started.assert_called_once()
    publisher.execution_finished.assert_called_once()
