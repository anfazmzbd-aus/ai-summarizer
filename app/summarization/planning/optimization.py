"""
V9.3-M5 deterministic resource optimization.

The optimizer is provider-independent and uses relative resource units.
No provider pricing, network calls, or LLM calls are involved.
"""

from __future__ import annotations

from app.summarization.strategies.models import (
    StrategySelection,
    SummarizationStrategyType,
)

from .optimization_models import (
    StrategyOptimizationDecision,
    StrategyOptimizationEstimate,
)


class StrategyResourceOptimizer:
    """
    Estimate and constrain resource usage deterministically.

    M5 deliberately uses relative cost units rather than provider-specific
    monetary pricing. This keeps the planning layer independent of OpenAI,
    Azure OpenAI, Ollama, or any other provider.
    """

    optimizer_version = "v9.3-m5"

    _OUTPUT_RATIO = 0.25

    _LATENCY_PER_1K = {
        SummarizationStrategyType.DIRECT: 100,
        SummarizationStrategyType.MAP_REDUCE: 180,
        SummarizationStrategyType.HIERARCHICAL: 260,
    }

    _COST_PER_1K = {
        SummarizationStrategyType.DIRECT: 1,
        SummarizationStrategyType.MAP_REDUCE: 2,
        SummarizationStrategyType.HIERARCHICAL: 3,
    }

    def estimate(
        self,
        strategy: SummarizationStrategyType,
        *,
        input_tokens: int,
        chunk_count: int,
    ) -> StrategyOptimizationEstimate:
        """Return a deterministic resource estimate."""

        if not isinstance(
            strategy,
            SummarizationStrategyType,
        ):
            raise TypeError("strategy must be a SummarizationStrategyType")

        if not isinstance(input_tokens, int) or input_tokens < 0:
            raise ValueError("input_tokens must be a non-negative integer")

        if not isinstance(chunk_count, int) or chunk_count < 0:
            raise ValueError("chunk_count must be a non-negative integer")

        output_tokens = int(round(input_tokens * self._OUTPUT_RATIO))

        total_tokens = input_tokens + output_tokens

        units = (
            max(
                1,
                (total_tokens + 999) // 1000,
            )
            if total_tokens
            else 0
        )

        latency = units * self._LATENCY_PER_1K[strategy]

        cost = units * self._COST_PER_1K[strategy]

        # Multi-stage strategies process intermediate summaries.
        # The surcharge is deterministic and provider-independent.
        if strategy is SummarizationStrategyType.MAP_REDUCE:
            latency += chunk_count * 20
            cost += chunk_count

        elif strategy is SummarizationStrategyType.HIERARCHICAL:
            latency += chunk_count * 35
            cost += chunk_count * 2

        rationale = (
            f"strategy={strategy.value}",
            f"input_tokens={input_tokens}",
            f"chunk_count={chunk_count}",
        )

        return StrategyOptimizationEstimate(
            strategy=strategy,
            input_tokens=input_tokens,
            chunk_count=chunk_count,
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            estimated_total_tokens=total_tokens,
            estimated_latency_ms=latency,
            estimated_cost_units=cost,
            rationale=rationale,
            metadata={
                "optimizer_version": self.optimizer_version,
                "output_ratio": self._OUTPUT_RATIO,
                "cost_unit": "relative",
                "latency_unit": "milliseconds",
            },
        )

    def decide(
        self,
        selection: StrategySelection,
        *,
        max_cost_units: int | None = None,
        max_latency_ms: int | None = None,
        max_total_tokens: int | None = None,
    ) -> StrategyOptimizationDecision:
        """
        Select a strategy satisfying the supplied resource constraints.

        The candidate set begins at the existing baseline strategy.
        M5 therefore never silently downgrades the V9.2/M4 strategy.
        """

        if not isinstance(
            selection,
            StrategySelection,
        ):
            raise TypeError("selection must be a StrategySelection")

        self._validate_limit(
            "max_cost_units",
            max_cost_units,
        )
        self._validate_limit(
            "max_latency_ms",
            max_latency_ms,
        )
        self._validate_limit(
            "max_total_tokens",
            max_total_tokens,
        )

        baseline = selection.strategy

        candidates = self._candidate_strategies(baseline)

        estimates = tuple(
            self.estimate(
                strategy,
                input_tokens=selection.token_count,
                chunk_count=selection.chunk_count,
            )
            for strategy in candidates
        )

        def fits(
            item: StrategyOptimizationEstimate,
        ) -> bool:
            return (
                (max_cost_units is None or item.estimated_cost_units <= max_cost_units)
                and (
                    max_latency_ms is None
                    or item.estimated_latency_ms <= max_latency_ms
                )
                and (
                    max_total_tokens is None
                    or item.estimated_total_tokens <= max_total_tokens
                )
            )

        baseline_estimate = next(
            item for item in estimates if item.strategy is baseline
        )

        constraints_supplied = any(
            value is not None
            for value in (
                max_cost_units,
                max_latency_ms,
                max_total_tokens,
            )
        )

        if fits(baseline_estimate):
            return StrategyOptimizationDecision(
                baseline_strategy=baseline,
                selected_strategy=baseline,
                estimates=estimates,
                reason=("baseline strategy satisfies " "resource constraints"),
                constrained=constraints_supplied,
                metadata=self._metadata(
                    max_cost_units,
                    max_latency_ms,
                    max_total_tokens,
                ),
            )

        feasible = [item for item in estimates if fits(item)]

        if feasible:
            selected = min(
                feasible,
                key=lambda item: (
                    item.estimated_total_tokens,
                    item.estimated_latency_ms,
                    item.estimated_cost_units,
                ),
            )

            return StrategyOptimizationDecision(
                baseline_strategy=baseline,
                selected_strategy=selected.strategy,
                estimates=estimates,
                reason=("selected the least-resource " "feasible strategy"),
                constrained=True,
                metadata=self._metadata(
                    max_cost_units,
                    max_latency_ms,
                    max_total_tokens,
                ),
            )

        return StrategyOptimizationDecision(
            baseline_strategy=baseline,
            selected_strategy=baseline,
            estimates=estimates,
            reason=(
                "no candidate satisfies all resource " "constraints; baseline retained"
            ),
            constrained=True,
            metadata={
                **self._metadata(
                    max_cost_units,
                    max_latency_ms,
                    max_total_tokens,
                ),
                "constraint_fallback": True,
            },
        )

    @staticmethod
    def _candidate_strategies(
        baseline: SummarizationStrategyType,
    ) -> tuple[SummarizationStrategyType, ...]:
        """
        Return baseline and strategies above it.

        M5 never downgrades a baseline decision.
        """

        order = (
            SummarizationStrategyType.DIRECT,
            SummarizationStrategyType.MAP_REDUCE,
            SummarizationStrategyType.HIERARCHICAL,
        )

        index = order.index(baseline)

        return order[index:]

    @staticmethod
    def _validate_limit(
        name: str,
        value: int | None,
    ) -> None:
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError(f"{name} must be a non-negative " "integer or None")

    def _metadata(
        self,
        cost: int | None,
        latency: int | None,
        tokens: int | None,
    ) -> dict[str, object]:
        return {
            "optimizer_version": self.optimizer_version,
            "max_cost_units": cost,
            "max_latency_ms": latency,
            "max_total_tokens": tokens,
        }
