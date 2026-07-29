"""
AI Summarizer V7.8 Runtime Session

Owns all runtime-scoped objects for a single execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.orchestration.execution.execution_context import ExecutionContext
from app.orchestration.graph.graph_schema import ExecutionGraph
from app.runtime.cancellation_token import CancellationToken
from app.runtime.intelligence.decision import Decision
from app.runtime.runtime_config import RuntimeConfig
from app.runtime.runtime_context import RuntimeContext
from app.runtime.runtime_metadata import RuntimeMetadata


@dataclass(slots=True)
class RuntimeSession:
    """
    Represents one runtime execution.

    Aggregates every runtime-scoped object.
    """

    config: RuntimeConfig = field(default_factory=RuntimeConfig)

    metadata: RuntimeMetadata = field(default_factory=RuntimeMetadata)

    cancellation_token: CancellationToken = field(default_factory=CancellationToken)

    execution_context: ExecutionContext = field(default_factory=ExecutionContext)

    runtime_context: RuntimeContext = field(init=False)

    #
    # V7.9 Phase 2 additions
    #

    execution_graph: ExecutionGraph | None = None

    decision: Decision | None = None

    execution_result: object | None = None

    def __post_init__(self) -> None:
        self.runtime_context = RuntimeContext(
            execution_context=self.execution_context,
            config=self.config,
            metadata=self.metadata,
            cancellation_token=self.cancellation_token,
        )
