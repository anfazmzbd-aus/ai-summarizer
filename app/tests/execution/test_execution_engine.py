from unittest.mock import Mock

from app.orchestration.execution.execution_engine import ExecutionEngine


def test_execute_accepts_none_decision():
    registry = Mock()
    contracts = Mock()

    engine = ExecutionEngine(
        registry,
        contracts,
    )

    graph = Mock()
    graph.layers = []

    validator = Mock()
    engine.validator = validator

    state = Mock()
    state.artifacts = {}

    result = engine.execute(
        graph,
        state,
        decision=None,
    )

    validator.validate.assert_called_once_with(graph)

    assert result.state is state


def test_execute_accepts_decision():
    registry = Mock()
    contracts = Mock()

    engine = ExecutionEngine(
        registry,
        contracts,
    )

    graph = Mock()
    graph.layers = []

    validator = Mock()
    engine.validator = validator

    state = Mock()
    state.artifacts = {}

    decision = Mock()
    decision.strategy = Mock()

    result = engine.execute(
        graph,
        state,
        decision=decision,
    )

    validator.validate.assert_called_once_with(graph)

    assert result.state is state


def test_decision_is_not_modified():
    registry = Mock()
    contracts = Mock()

    engine = ExecutionEngine(
        registry,
        contracts,
    )

    graph = Mock()
    graph.layers = []

    validator = Mock()
    engine.validator = validator

    state = Mock()
    state.artifacts = {}

    decision = Mock()
    original_strategy = decision.strategy

    engine.execute(
        graph,
        state,
        decision=decision,
    )

    assert decision.strategy is original_strategy


def test_parallel_execution_enabled_from_decision():
    registry = Mock()
    contracts = Mock()

    engine = ExecutionEngine(registry, contracts)

    graph = Mock()
    graph.layers = []

    engine.validator = Mock()

    state = Mock()
    state.artifacts = {}

    decision = Mock()
    decision.strategy.parallel_execution = True

    original = engine.layer_executor._config.parallel_execution

    engine.execute(graph, state, decision=decision)

    assert engine.layer_executor._config.parallel_execution == original


def test_parallel_execution_disabled_from_decision():
    registry = Mock()
    contracts = Mock()

    engine = ExecutionEngine(registry, contracts)

    graph = Mock()
    graph.layers = []

    engine.validator = Mock()

    state = Mock()
    state.artifacts = {}

    decision = Mock()
    decision.strategy.parallel_execution = False

    original = engine.layer_executor._config.parallel_execution

    engine.execute(graph, state, decision=decision)

    assert engine.layer_executor._config.parallel_execution == original
