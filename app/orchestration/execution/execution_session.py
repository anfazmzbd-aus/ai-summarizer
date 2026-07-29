"""
AI Summarizer V7.9 Execution Session

Represents one complete runtime execution lifecycle.

The ExecutionSession composes:

    ExecutionGraph
          +
    ExecutionContext
          +
    Decision

It does not execute runtime operations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.orchestration.execution.execution_context import (
    ExecutionContext,
)
from app.orchestration.graph.graph_schema import (
    ExecutionGraph,
)
from app.runtime.intelligence.decision import (
    Decision,
)


@dataclass(slots=True)
class ExecutionSession:
    """
    Runtime container for a single execution.

    Responsibilities:
        - Hold execution graph
        - Hold runtime context
        - Hold optional execution decision
        - Track session creation time

    Non-responsibilities:
        - Execute graph
        - Schedule nodes
        - Select strategies
        - Mutate decisions
    """

    execution_graph: ExecutionGraph

    execution_context: ExecutionContext

    decision: Decision | None = None

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
