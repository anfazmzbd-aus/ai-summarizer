"""
AI Summarizer V7.8 Runtime Manager

Coordinates runtime execution while delegating node execution
to the existing V7.7 ExecutionEngine.
"""

from __future__ import annotations

from app.orchestration.execution.execution_engine import ExecutionEngine

from .runtime_context import RuntimeContext


class RuntimeManager:
    """
    Entry point for runtime execution.

    Owns runtime lifecycle management while delegating execution
    to the underlying ExecutionEngine.
    """

    def __init__(self, execution_engine: ExecutionEngine) -> None:
        self._execution_engine = execution_engine

    @property
    def execution_engine(self) -> ExecutionEngine:
        """Returns the configured execution engine."""
        return self._execution_engine

    def execute(self, context: RuntimeContext):
        """
        Execute a runtime context.

        CP-1 implementation simply delegates to the existing
        execution engine.

        Future phases will introduce:

        - lifecycle transitions
        - retries
        - events
        - metrics
        - tracing
        """

        return self._execution_engine.execute(context.execution_context)
