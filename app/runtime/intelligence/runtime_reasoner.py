"""
AI Summarizer V7.9 Runtime Reasoner

Analyzes runtime execution context and produces
a deterministic ReasoningResult.

This component is advisory only.
It does not modify runtime state or control execution.
"""

from __future__ import annotations

from app.orchestration.execution.execution_context import ExecutionContext

from .reasoning_result import ReasoningResult


class RuntimeReasoner:
    """
    Converts ExecutionContext observations into ReasoningResult.

    Responsibilities:
        - Analyze runtime state
        - Extract execution signals
        - Produce deterministic reasoning output

    Non-responsibilities:
        - Strategy selection
        - Execution control
        - Runtime mutation
    """

    def reason(
        self,
        context: ExecutionContext,
    ) -> ReasoningResult:
        """
        Analyze runtime context.

        Args:
            context:
                Current runtime execution context.

        Returns:
            Immutable ReasoningResult.
        """

        if context is None:
            raise ValueError("ExecutionContext cannot be None")

        return ReasoningResult(
            workload_size=self._collect_workload(context),
            estimated_parallelism=self._collect_parallelism(context),
            cache_available=self._collect_cache_state(context),
            cancellation_requested=self._collect_cancellation(context),
            timeout_risk=self._collect_timeout_risk(context),
            retry_pressure=self._collect_retry_pressure(context),
            policy_restricted=self._collect_policy_state(context),
        )

    def _collect_workload(
        self,
        context: ExecutionContext,
    ) -> int:
        """
        Calculate workload size from execution graph.
        """

        graph = getattr(context, "execution_graph", None)

        if graph is None:
            return 0

        nodes = getattr(graph, "nodes", None)

        if nodes is None:
            return 0

        return len(nodes)

    def _collect_parallelism(
        self,
        context: ExecutionContext,
    ) -> int:
        """
        Estimate maximum parallel execution capacity.
        """

        graph = getattr(context, "execution_graph", None)

        if graph is None:
            return 1

        layers = getattr(graph, "layers", None)

        if not layers:
            return 1

        return max(len(layer) for layer in layers)

    def _collect_cache_state(
        self,
        context: ExecutionContext,
    ) -> bool:
        """
        Determine cache availability.
        """

        cache = getattr(context, "runtime_cache", None)

        if cache is None:
            return False

        return bool(getattr(cache, "enabled", False))

    def _collect_cancellation(
        self,
        context: ExecutionContext,
    ) -> bool:
        """
        Determine cancellation state.
        """

        token = getattr(
            context,
            "cancellation_token",
            None,
        )

        if token is None:
            return False

        return bool(getattr(token, "is_cancelled", False))

    def _collect_timeout_risk(
        self,
        context: ExecutionContext,
    ) -> bool:
        """
        Detect timeout risk from runtime metadata.
        """

        metadata = getattr(
            context,
            "runtime_metadata",
            None,
        )

        if metadata is None:
            return False

        return bool(
            getattr(
                metadata,
                "timeout_risk",
                False,
            )
        )

    def _collect_retry_pressure(
        self,
        context: ExecutionContext,
    ) -> bool:
        """
        Detect retry pressure.
        """

        metadata = getattr(
            context,
            "runtime_metadata",
            None,
        )

        if metadata is None:
            return False

        return bool(
            getattr(
                metadata,
                "retry_pressure",
                False,
            )
        )

    def _collect_policy_state(
        self,
        context: ExecutionContext,
    ) -> bool:
        """
        Detect runtime policy restrictions.
        """

        policy = getattr(
            context,
            "policy_engine",
            None,
        )

        if policy is None:
            return False

        return bool(
            getattr(
                policy,
                "restricted",
                False,
            )
        )
