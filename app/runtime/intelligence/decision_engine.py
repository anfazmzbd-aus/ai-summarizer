"""
AI Summarizer V7.9 Decision Engine

Coordinates the Adaptive Runtime Intelligence pipeline.

Pipeline:

ExecutionContext
        │
        ▼
RuntimeReasoner
        │
        ▼
ReasoningResult
        │
        ▼
StrategySelector
        │
        ▼
ExecutionStrategy
        │
        ▼
Decision
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.orchestration.execution.execution_context import ExecutionContext

from .decision import Decision
from .execution_strategy import ExecutionStrategy
from .reasoning_result import ReasoningResult
from .runtime_reasoner import RuntimeReasoner
from .strategy_selector import StrategySelector


class DecisionEngine:
    """
    Coordinates runtime reasoning and strategy selection.

    Responsibilities:
        - Analyze runtime context
        - Select execution strategy
        - Produce immutable Decision

    Non-responsibilities:
        - Execute runtime
        - Modify runtime state
        - Invoke Scheduler
        - Invoke ExecutionEngine
    """

    def __init__(
        self,
        runtime_reasoner: RuntimeReasoner | None = None,
        strategy_selector: StrategySelector | None = None,
    ) -> None:
        self._runtime_reasoner = runtime_reasoner or RuntimeReasoner()
        self._strategy_selector = strategy_selector or StrategySelector()

    def decide(
        self,
        context: ExecutionContext,
    ) -> Decision:
        """
        Produce a runtime execution decision.

        Args:
            context:
                Current execution context.

        Returns:
            Immutable Decision.
        """

        if context is None:
            raise ValueError("ExecutionContext cannot be None")

        reasoning = self._runtime_reasoner.reason(context)

        strategy = self._strategy_selector.select(reasoning)

        return self._build_decision(
            reasoning=reasoning,
            strategy=strategy,
        )

    def _build_decision(
        self,
        *,
        reasoning: ReasoningResult,
        strategy: ExecutionStrategy,
    ) -> Decision:
        """
        Construct immutable decision.
        """

        return Decision(
            strategy=strategy,
            reasoning=reasoning,
            created_at=datetime.now(UTC),
        )
