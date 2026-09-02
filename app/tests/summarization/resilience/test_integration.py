from __future__ import annotations

import pytest

from app.summarization.chunking.text_chunker import TextChunker
from app.summarization.resilience import (
    FallbackAction,
    FallbackDecision,
    ResilientExecutionPlanner,
)
from app.summarization.resilience.integration import (
    ResilientStrategyExecutionBoundary,
)
from app.summarization.strategies.execution import StrategyExecutor
from app.summarization.strategies.models import (
    StrategyExecutionResult,
    SummarizationStrategyType,
)


def make_chunks(text: str = "source text"):
    return tuple(TextChunker().chunk(text))


def test_successful_execution_preserves_existing_result() -> None:
    boundary = ResilientStrategyExecutionBoundary(
        executor=StrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute(
        strategy=SummarizationStrategyType.DIRECT,
        chunks=make_chunks(),
        summarize=lambda text: f"summary:{text}",
    )

    assert isinstance(result, StrategyExecutionResult)
    assert result.content == "summary:source text"


def test_execution_failure_becomes_existing_resilience_decision() -> None:
    class FailingStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            raise RuntimeError("m7.2.1 execution failure")

    boundary = ResilientStrategyExecutionBoundary(
        executor=FailingStrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        chunks=make_chunks(),
        summarize=lambda text: text,
    )

    assert isinstance(result, FallbackDecision)
    assert result.action is FallbackAction.FALLBACK
    assert result.fallback_strategy is SummarizationStrategyType.MAP_REDUCE

    assert result.failure.error_type == "RuntimeError"
    assert result.failure.message == "m7.2.1 execution failure"
    assert result.failure.strategy is SummarizationStrategyType.HIERARCHICAL
    assert result.failure.attempt == 1
    assert result.failure.retryable is True


def test_failure_boundary_does_not_execute_fallback_strategy() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class FailingStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)
            raise RuntimeError("single execution failure")

    boundary = ResilientStrategyExecutionBoundary(
        executor=FailingStrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        chunks=make_chunks(),
        summarize=lambda text: text,
    )

    assert isinstance(result, FallbackDecision)

    assert executed_strategies == [
        SummarizationStrategyType.HIERARCHICAL,
    ]


def test_boundary_rejects_invalid_resilience_dependencies() -> None:
    with pytest.raises(
        TypeError,
        match="executor must be a StrategyExecutor",
    ):
        ResilientStrategyExecutionBoundary(
            executor=object(),  # type: ignore[arg-type]
            resilience_planner=ResilientExecutionPlanner(),
        )

    with pytest.raises(
        TypeError,
        match="resilience_planner must be a ResilientExecutionPlanner",
    ):
        ResilientStrategyExecutionBoundary(
            executor=StrategyExecutor(),
            resilience_planner=object(),  # type: ignore[arg-type]
        )


def test_fallback_decision_executes_exactly_one_planned_strategy() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class RecordingStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)

            if strategy is SummarizationStrategyType.HIERARCHICAL:
                raise RuntimeError("hierarchical failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    boundary = ResilientStrategyExecutionBoundary(
        executor=RecordingStrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute_with_fallback(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        chunks=make_chunks(),
        summarize=lambda text: f"recovered:{text}",
    )

    assert isinstance(result, StrategyExecutionResult)

    assert executed_strategies == [
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    ]


def test_retry_decision_executes_same_strategy_exactly_once() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class RecordingStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)

            if len(executed_strategies) == 1:
                raise RuntimeError("first direct execution failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    boundary = ResilientStrategyExecutionBoundary(
        executor=RecordingStrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute_with_retry(
        strategy=SummarizationStrategyType.DIRECT,
        chunks=make_chunks(),
        summarize=lambda text: f"recovered:{text}",
    )

    assert isinstance(result, StrategyExecutionResult)

    assert executed_strategies == [
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.DIRECT,
    ]


def test_terminate_decision_does_not_execute_again() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class AlwaysFailingExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)
            raise RuntimeError("terminal failure")

    boundary = ResilientStrategyExecutionBoundary(
        executor=AlwaysFailingExecutor(),
        resilience_planner=ResilientExecutionPlanner(
            max_attempts=1,
        ),
    )

    result = boundary.execute_with_retry(
        strategy=SummarizationStrategyType.DIRECT,
        chunks=make_chunks(),
        summarize=lambda text: text,
    )

    assert isinstance(result, FallbackDecision)
    assert result.action is FallbackAction.TERMINATE

    assert executed_strategies == [
        SummarizationStrategyType.DIRECT,
    ]


def test_fallback_second_failure_is_not_recursively_recovered() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class AlwaysFailingExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)
            raise RuntimeError(f"{strategy.value} failed")

    boundary = ResilientStrategyExecutionBoundary(
        executor=AlwaysFailingExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    with pytest.raises(
        RuntimeError,
        match="map_reduce failed",
    ):
        boundary.execute_with_fallback(
            strategy=SummarizationStrategyType.HIERARCHICAL,
            chunks=make_chunks(),
            summarize=lambda text: text,
        )

    assert executed_strategies == [
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    ]


def test_unified_recovery_executes_existing_recovery_decision() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class RecordingStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)

            if strategy is SummarizationStrategyType.HIERARCHICAL:
                raise RuntimeError("hierarchical failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    boundary = ResilientStrategyExecutionBoundary(
        executor=RecordingStrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute_with_recovery(
        strategy=SummarizationStrategyType.HIERARCHICAL,
        chunks=make_chunks(),
        summarize=lambda text: f"recovered:{text}",
    )

    assert isinstance(result, StrategyExecutionResult)

    assert executed_strategies == [
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    ]


def test_unified_recovery_executes_retry_once() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class RecordingStrategyExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)

            if len(executed_strategies) == 1:
                raise RuntimeError("first direct execution failure")

            return super().execute(
                strategy,
                chunks,
                summarize,
            )

    boundary = ResilientStrategyExecutionBoundary(
        executor=RecordingStrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    result = boundary.execute_with_recovery(
        strategy=SummarizationStrategyType.DIRECT,
        chunks=make_chunks(),
        summarize=lambda text: f"recovered:{text}",
    )

    assert isinstance(result, StrategyExecutionResult)

    assert executed_strategies == [
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.DIRECT,
    ]


def test_unified_recovery_preserves_terminate_decision() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class AlwaysFailingExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)
            raise RuntimeError("terminal failure")

    boundary = ResilientStrategyExecutionBoundary(
        executor=AlwaysFailingExecutor(),
        resilience_planner=ResilientExecutionPlanner(
            max_attempts=1,
        ),
    )

    result = boundary.execute_with_recovery(
        strategy=SummarizationStrategyType.DIRECT,
        chunks=make_chunks(),
        summarize=lambda text: text,
    )

    assert isinstance(result, FallbackDecision)
    assert result.action is FallbackAction.TERMINATE

    assert executed_strategies == [
        SummarizationStrategyType.DIRECT,
    ]


def test_unified_recovery_does_not_retry_summarizer_callback_failure() -> None:
    summarize_calls = 0

    def failing_summarize(text: str) -> str:
        nonlocal summarize_calls
        summarize_calls += 1
        raise RuntimeError("summarizer failure")

    boundary = ResilientStrategyExecutionBoundary(
        executor=StrategyExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    with pytest.raises(
        RuntimeError,
        match="summarizer failure",
    ):
        boundary.execute_with_recovery(
            strategy=SummarizationStrategyType.DIRECT,
            chunks=make_chunks(),
            summarize=failing_summarize,
        )

    assert summarize_calls == 1


def test_unified_recovery_fallback_failure_does_not_recover_again() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class AlwaysFailingExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)
            raise RuntimeError(f"{strategy.value} failed")

    boundary = ResilientStrategyExecutionBoundary(
        executor=AlwaysFailingExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    with pytest.raises(
        RuntimeError,
        match="map_reduce failed",
    ):
        boundary.execute_with_recovery(
            strategy=SummarizationStrategyType.HIERARCHICAL,
            chunks=make_chunks(),
            summarize=lambda text: text,
        )

    assert executed_strategies == [
        SummarizationStrategyType.HIERARCHICAL,
        SummarizationStrategyType.MAP_REDUCE,
    ]


def test_unified_recovery_retry_failure_does_not_retry_again() -> None:
    executed_strategies: list[SummarizationStrategyType] = []

    class AlwaysFailingExecutor(StrategyExecutor):
        def execute(
            self,
            strategy,
            chunks,
            summarize,
        ):
            executed_strategies.append(strategy)
            raise RuntimeError("direct failed")

    boundary = ResilientStrategyExecutionBoundary(
        executor=AlwaysFailingExecutor(),
        resilience_planner=ResilientExecutionPlanner(),
    )

    with pytest.raises(
        RuntimeError,
        match="direct failed",
    ):
        boundary.execute_with_recovery(
            strategy=SummarizationStrategyType.DIRECT,
            chunks=make_chunks(),
            summarize=lambda text: text,
        )

    assert executed_strategies == [
        SummarizationStrategyType.DIRECT,
        SummarizationStrategyType.DIRECT,
    ]
