"""
AI Summarizer V7.8 Runtime Context

Defines the top-level runtime container for a single execution.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.orchestration.execution.execution_context import ExecutionContext

from .cancellation_token import CancellationToken
from .runtime_config import RuntimeConfig
from .runtime_metadata import RuntimeMetadata


@dataclass(slots=True)
class RuntimeContext:
    """
    Top-level runtime context.

    Owns every runtime-scoped object associated with a single execution.
    """

    execution_context: ExecutionContext

    config: RuntimeConfig

    metadata: RuntimeMetadata

    cancellation_token: CancellationToken
