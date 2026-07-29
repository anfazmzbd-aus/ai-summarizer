from datetime import datetime
from unittest.mock import Mock, patch

from app.runtime.intelligence.decision import Decision
from app.runtime.intelligence.execution_strategy import ExecutionStrategy
from app.runtime.intelligence.reasoning_result import ReasoningResult
from app.runtime.intelligence.strategy_types import ExecutionStrategyType
from app.runtime.runtime_manager import RuntimeManager


def make_state():
    state = Mock()
    state.artifacts = {}
    state.node_outputs = {}
    return state


def make_plan():
    graph = Mock()
    graph.layers = []

    plan = Mock()
    plan.graph = graph
    return plan


def make_execution_result():
    result = Mock()
    result.state = make_state()
    result.outputs = {}
    return result


def make_decision(parallel=False):
    return Decision(
        strategy=ExecutionStrategy(
            strategy=ExecutionStrategyType.DEFAULT,
            parallel_execution=parallel,
            use_cache=False,
            enable_retry=False,
            checkpoint_enabled=False,
            timeout_multiplier=1.0,
        ),
        reasoning=ReasoningResult(
            workload_size=10,
            estimated_parallelism=2,
            cache_available=False,
            cancellation_requested=False,
            timeout_risk=False,
            retry_pressure=False,
            policy_restricted=False,
        ),
        created_at=datetime.utcnow(),
    )


def test_pipeline_without_decision_engine():
    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.side_effect = [
        make_execution_result(),
        make_execution_result(),
    ]

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
    )

    manager.run(
        text="hello",
        contracts={},
        state=make_state(),
    )

    execution_engine.execute.assert_called_once()

    _, kwargs = execution_engine.execute.call_args

    assert kwargs["decision"] is None


def test_pipeline_with_decision_engine():
    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.side_effect = [
        make_execution_result(),
        make_execution_result(),
    ]

    decision_engine = Mock()
    decision_engine.decide.return_value = make_decision()

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
        decision_engine=decision_engine,
    )

    manager.run(
        text="hello",
        contracts={},
        state=make_state(),
    )

    decision_engine.decide.assert_called_once()

    _, kwargs = execution_engine.execute.call_args

    assert kwargs["decision"] is not None


def test_parallel_strategy_reaches_execution_engine():
    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.side_effect = [
        make_execution_result(),
        make_execution_result(),
    ]

    decision = make_decision(parallel=True)

    decision_engine = Mock()
    decision_engine.decide.return_value = decision

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
        decision_engine=decision_engine,
    )

    manager.run(
        text="hello",
        contracts={},
        state=make_state(),
    )

    _, kwargs = execution_engine.execute.call_args

    assert kwargs["decision"].strategy.parallel_execution is True


def test_runtime_pipeline_handles_empty_graph():
    scheduler = Mock()

    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.side_effect = [
        make_execution_result(),
        make_execution_result(),
    ]

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
    )

    result = manager.run(
        text="hello",
        contracts={},
        state=make_state(),
    )

    assert result is not None


def test_runtime_pipeline_preserves_execution_result():
    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution = make_execution_result()

    execution_engine = Mock()
    execution_engine.execute.return_value = execution

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
    )

    result = manager.run(
        text="hello",
        contracts={},
        state=make_state(),
    )

    assert result is execution


def test_pipeline_multiple_executions_are_isolated():
    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.side_effect = [
        make_execution_result(),
        make_execution_result(),
    ]

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
    )

    state = make_state()

    result1 = manager.run(
        text="first",
        contracts={},
        state=state,
    )

    result2 = manager.run(
        text="second",
        contracts={},
        state=state,
    )

    assert result1 is not result2


def test_decision_propagates_to_execution_engine():
    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.side_effect = [
        make_execution_result(),
        make_execution_result(),
    ]

    decision = make_decision()

    decision_engine = Mock()
    decision_engine.decide.return_value = decision

    manager = RuntimeManager(
        scheduler=scheduler,
        execution_engine=execution_engine,
        decision_engine=decision_engine,
    )

    manager.run(
        text="hello",
        contracts={},
        state=make_state(),
    )

    _, kwargs = execution_engine.execute.call_args

    assert kwargs["decision"] is decision


def test_runtime_manager_executes_middleware():

    scheduler = Mock()
    scheduler.schedule.return_value = make_plan()

    execution_engine = Mock()
    execution_engine.execute.return_value = make_execution_result()

    with patch("app.runtime.runtime_manager.MiddlewarePipeline") as middleware:

        manager = RuntimeManager(
            scheduler=scheduler,
            execution_engine=execution_engine,
        )

        manager.run(
            text="hello",
            contracts={},
            state=make_state(),
        )

        pipeline = middleware.return_value

        pipeline.before_execution.assert_called_once()
        pipeline.after_execution.assert_called_once()
