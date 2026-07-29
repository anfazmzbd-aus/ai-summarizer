"""
AI Summarizer V7.8 Runtime Manager

Coordinates runtime execution while delegating node execution
to the existing V7.7 ExecutionEngine.
"""

from __future__ import annotations

from app.orchestration.execution.execution_engine import ExecutionEngine
from app.orchestration.scheduler.scheduler import Scheduler
from app.runtime.middleware_pipeline import MiddlewarePipeline

from .runtime_session import RuntimeSession


class RuntimeManager:
    """
    Entry point for runtime execution.

    Owns runtime lifecycle management while delegating execution
    to the underlying ExecutionEngine.
    """

    """"
    CP-2 implementation:
    Coordinates the runtime lifecycle.
    """

    def __init__(
        self,
        scheduler: Scheduler,
        execution_engine: ExecutionEngine,
        decision_engine=None,
    ) -> None:
        self._scheduler = scheduler
        self._execution_engine = execution_engine
        self._decision_engine = decision_engine

    @property
    def execution_engine(self) -> ExecutionEngine:
        """Returns the configured execution engine."""
        return self._execution_engine

    @property
    def scheduler(self):
        return self._scheduler

    def run(
        self,
        *,
        text: str,
        contracts,
        state,
    ):
        """
        Execute a complete runtime cycle.

        CP-2 implementation:
        - schedule
        - create RuntimeContext
        - execute
        """

        # Context is created now for lifecycle ownership.
        session = RuntimeSession()

        context = session.runtime_context

        context.mark_initializing()

        plan = self._scheduler.schedule(
            text,
            contracts,
        )

        session.execution_graph = plan.graph

        if self._decision_engine:
            session.decision = self._decision_engine.decide(session.execution_context)

        context.mark_scheduling()

        context.mark_executing()

        self.pipeline = MiddlewarePipeline()
        self.pipeline.before_execution(context)

        # ExecutionEngine still uses the existing V7.7 API.
        try:
            execution = self._execution_engine.execute(
                plan.graph,
                state,
                decision=session.decision,  # V7.9 Phase 2 Runtime intelligence integration.
            )
            session.execution_result = execution
        except Exception:
            context.mark_failed()
            raise
        finally:
            context.mark_completed()

        self.pipeline.after_execution(
            context,
            execution,
        )

        return execution
