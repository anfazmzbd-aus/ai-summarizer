"""
AI Summarizer V7.8 Node Execution Result
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class NodeExecutionResult:
    """
    Immutable result produced by a node execution.
    """

    node: str

    output: dict[str, Any]
