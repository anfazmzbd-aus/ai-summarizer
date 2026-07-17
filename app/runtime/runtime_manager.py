"""
AI Summarizer V7.8 Runtime Manager

Coordinates runtime execution while delegating node execution
to the existing V7.7 ExecutionEngine.
"""

from __future__ import annotations

from app.orchestration.execution.execution_engine import ExecutionEngine
from app.orchestration.scheduler.scheduler import Scheduler

# from .cancellation_token import CancellationToken
# from .runtime_config import RuntimeConfig
# from .runtime_context import RuntimeContext
# from .runtime_metadata import RuntimeMetadata


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
    ) -> None:
        self._scheduler = scheduler
        self._execution_engine = execution_engine

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

        plan = self._scheduler.schedule(text, contracts)

        # Context is created now for lifecycle ownership.
        # ExecutionEngine still uses the existing V7.7 API.
        execution = self._execution_engine.execute(
            plan.graph,
            state,
        )

        return execution
