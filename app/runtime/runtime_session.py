"""
AI Summarizer V7.8 Runtime Session

Owns all runtime-scoped objects for a single execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.orchestration.execution.execution_context import ExecutionContext

from .cancellation_token import CancellationToken
from .runtime_config import RuntimeConfig
from .runtime_context import RuntimeContext
from .runtime_metadata import RuntimeMetadata


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

    def __post_init__(self) -> None:
        self.runtime_context = RuntimeContext(
            execution_context=self.execution_context,
            config=self.config,
            metadata=self.metadata,
            cancellation_token=self.cancellation_token,
        )
