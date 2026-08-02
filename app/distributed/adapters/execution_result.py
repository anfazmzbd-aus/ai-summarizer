"""
AI Summarizer V8.0

Remote execution result.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RemoteExecutionResult:

    success: bool

    output: Any = None

    error: str | None = None

    worker_id: str | None = None

    execution_time: float = 0.0
