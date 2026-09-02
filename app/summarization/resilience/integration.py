from __future__ import annotations

from collections.abc import Callable

from app.summarization.strategies.execution import StrategyExecutor
from app.summarization.strategies.models import (
    StrategyExecutionResult,
    SummarizationStrategyType,
)

from .executor import ResilientExecutionPlanner

from .models import (
    FallbackAction,
    FallbackDecision,
)

from dataclasses import dataclass


@dataclass(frozen=True)
class ResilientExecutionResult:
    execution: StrategyExecutionResult
    recovery_occurred: bool
    recovery_action: FallbackAction | None = None
    recovery_strategy: SummarizationStrategyType | None = None


class _SummarizerCallbackError(Exception):
    """Internal marker for failures originating in the summarize callback."""

    def __init__(self, original: Exception) -> None:
        super().__init__(str(original))
        self.original = original


class ResilientStrategyExecutionBoundary:
    """
    Integrate strategy execution failures with the existing V9.3
    resilience decision contract.

    The boundary preserves the existing resilience planner as the authority
    for recovery decisions and provides bounded execution helpers for a
    single planned fallback or retry action. It does not perform recursive
    recovery, provider switching, or unbounded retry loops.
    """

    def __init__(
        self,
        *,
        executor: StrategyExecutor,
        resilience_planner: ResilientExecutionPlanner,
    ) -> None:
        if not isinstance(executor, StrategyExecutor):
            raise TypeError("executor must be a StrategyExecutor")

        if not isinstance(
            resilience_planner,
            ResilientExecutionPlanner,
        ):
            raise TypeError("resilience_planner must be a ResilientExecutionPlanner")

        self._executor = executor
        self._resilience_planner = resilience_planner

    def execute(
        self,
        *,
        strategy: SummarizationStrategyType,
        chunks,
        summarize: Callable[[str], str],
    ) -> StrategyExecutionResult | FallbackDecision:
        def guarded_summarize(text: str) -> str:
            try:
                return summarize(text)
            except Exception as exc:
                raise _SummarizerCallbackError(exc) from exc

        try:
            return self._executor.execute(
                strategy,
                chunks,
                guarded_summarize,
            )
        except _SummarizerCallbackError as exc:
            raise exc.original from None
        except Exception as exc:
            return self._resilience_planner.decide_from_exception(
                strategy=strategy,
                exception=exc,
                attempt=1,
                attempted_strategies=(strategy,),
                retryable=True,
            )

    def execute_with_fallback(
        self,
        *,
        strategy: SummarizationStrategyType,
        chunks,
        summarize: Callable[[str], str],
    ) -> StrategyExecutionResult | FallbackDecision:
        """
        Execute the requested strategy and, when the existing resilience
        planner explicitly selects FALLBACK, execute exactly one planned
        fallback strategy.

        RETRY and TERMINATE decisions remain decisions only in M7.2.2.
        A failure during fallback execution is propagated and is not
        recursively recovered here.
        """

        result = self.execute(
            strategy=strategy,
            chunks=chunks,
            summarize=summarize,
        )

        if isinstance(result, StrategyExecutionResult):
            return result

        if result.action is not FallbackAction.FALLBACK:
            return result

        if result.fallback_strategy is None:
            raise ValueError("FALLBACK decision must provide a fallback strategy")

        return self._executor.execute(
            result.fallback_strategy,
            chunks,
            summarize,
        )

    def execute_with_retry(
        self,
        *,
        strategy: SummarizationStrategyType,
        chunks,
        summarize: Callable[[str], str],
    ) -> StrategyExecutionResult | FallbackDecision:
        """
        Execute the requested strategy and, when the existing resilience
        planner explicitly selects RETRY, execute the same strategy exactly
        one additional time.

        FALLBACK and TERMINATE remain decisions only in M7.2.3.
        A failure during the retry execution is propagated and is not
        recursively recovered here.
        """

        result = self.execute(
            strategy=strategy,
            chunks=chunks,
            summarize=summarize,
        )

        if isinstance(result, StrategyExecutionResult):
            return result

        if result.action is not FallbackAction.RETRY:
            return result

        return self._executor.execute(
            strategy,
            chunks,
            summarize,
        )

    def execute_with_recovery(
        self,
        *,
        strategy: SummarizationStrategyType,
        chunks,
        summarize: Callable[[str], str],
    ) -> StrategyExecutionResult | FallbackDecision:
        """
        Execute the requested strategy and apply exactly one recovery action
        selected by the existing V9.3 resilience planner.

        FALLBACK executes one planned fallback strategy.
        RETRY executes the same strategy exactly once more.
        TERMINATE remains a decision and stops execution.

        Failures during the recovery execution are propagated and are not
        recursively recovered here.
        """

        result = self.execute(
            strategy=strategy,
            chunks=chunks,
            summarize=summarize,
        )

        if isinstance(result, StrategyExecutionResult):
            return result

        if result.action is FallbackAction.FALLBACK:
            if result.fallback_strategy is None:
                raise ValueError("FALLBACK decision must provide a fallback strategy")

            return self._executor.execute(
                result.fallback_strategy,
                chunks,
                summarize,
            )

        if result.action is FallbackAction.RETRY:
            return self._executor.execute(
                strategy,
                chunks,
                summarize,
            )

        return result

    def execute_with_recovery_result(
        self,
        *,
        strategy: SummarizationStrategyType,
        chunks,
        summarize: Callable[[str], str],
    ) -> ResilientExecutionResult | FallbackDecision:
        result = self.execute(
            strategy=strategy,
            chunks=chunks,
            summarize=summarize,
        )

        if isinstance(result, StrategyExecutionResult):
            return ResilientExecutionResult(
                execution=result,
                recovery_occurred=False,
            )

        if result.action is FallbackAction.FALLBACK:
            if result.fallback_strategy is None:
                raise ValueError("FALLBACK decision must provide a fallback strategy")

            execution = self._executor.execute(
                result.fallback_strategy,
                chunks,
                summarize,
            )

            return ResilientExecutionResult(
                execution=execution,
                recovery_occurred=True,
                recovery_action=FallbackAction.FALLBACK,
                recovery_strategy=result.fallback_strategy,
            )

        if result.action is FallbackAction.RETRY:
            execution = self._executor.execute(
                strategy,
                chunks,
                summarize,
            )

            return ResilientExecutionResult(
                execution=execution,
                recovery_occurred=True,
                recovery_action=FallbackAction.RETRY,
                recovery_strategy=strategy,
            )

        return result


__all__ = [
    "ResilientStrategyExecutionBoundary",
]
