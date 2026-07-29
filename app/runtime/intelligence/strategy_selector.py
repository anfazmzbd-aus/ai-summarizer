"""
AI Summarizer V7.9 Strategy Selector

Maps runtime reasoning into an immutable execution strategy.

This component is deterministic and side-effect free.
"""

from __future__ import annotations

from .execution_strategy import ExecutionStrategy
from .reasoning_result import ReasoningResult
from .strategy_types import ExecutionStrategyType


class StrategySelector:
    """
    Select an execution strategy from runtime reasoning.

    Responsibilities:
        - Evaluate runtime observations
        - Apply strategy precedence
        - Produce immutable ExecutionStrategy

    Non-responsibilities:
        - Runtime analysis
        - Execution control
        - Runtime mutation
    """

    def select(
        self,
        reasoning: ReasoningResult,
    ) -> ExecutionStrategy:
        """
        Select an execution strategy.

        Args:
            reasoning:
                Runtime observations.

        Returns:
            Immutable execution strategy.
        """

        if reasoning is None:
            raise ValueError("ReasoningResult cannot be None")

        strategy_type = self._select_strategy_type(reasoning)

        return self._build_strategy(strategy_type)

    def _select_strategy_type(
        self,
        reasoning: ReasoningResult,
    ) -> ExecutionStrategyType:
        """
        Determine the execution strategy using
        deterministic precedence rules.
        """

        if reasoning.cancellation_requested:
            return ExecutionStrategyType.RECOVERY

        if reasoning.policy_restricted:
            return ExecutionStrategyType.CONSERVATIVE

        if reasoning.retry_pressure:
            return ExecutionStrategyType.RECOVERY

        if reasoning.timeout_risk:
            return ExecutionStrategyType.RECOVERY

        if reasoning.estimated_parallelism > 1:
            return ExecutionStrategyType.BALANCED

        return ExecutionStrategyType.DEFAULT

    def _build_strategy(
        self,
        strategy_type: ExecutionStrategyType,
    ) -> ExecutionStrategy:
        """
        Build an immutable execution strategy profile.
        """

        if strategy_type == ExecutionStrategyType.DEFAULT:
            return ExecutionStrategy(
                strategy=strategy_type,
                parallel_execution=True,
                use_cache=True,
                enable_retry=True,
                checkpoint_enabled=False,
                timeout_multiplier=1.0,
            )

        if strategy_type == ExecutionStrategyType.BALANCED:
            return ExecutionStrategy(
                strategy=strategy_type,
                parallel_execution=True,
                use_cache=True,
                enable_retry=True,
                checkpoint_enabled=True,
                timeout_multiplier=1.0,
            )

        if strategy_type == ExecutionStrategyType.CONSERVATIVE:
            return ExecutionStrategy(
                strategy=strategy_type,
                parallel_execution=False,
                use_cache=True,
                enable_retry=True,
                checkpoint_enabled=True,
                timeout_multiplier=1.25,
            )

        if strategy_type == ExecutionStrategyType.RECOVERY:
            return ExecutionStrategy(
                strategy=strategy_type,
                parallel_execution=False,
                use_cache=True,
                enable_retry=True,
                checkpoint_enabled=True,
                timeout_multiplier=2.0,
            )

        raise ValueError(f"Unsupported strategy type: {strategy_type}")
