"""
AI Summarizer V8.0

Distributed trace context.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(slots=True)
class TraceContext:
    """
    Carries execution correlation metadata.
    """

    trace_id: UUID

    parent_span_id: UUID | None = None

    @classmethod
    def create(
        cls,
    ) -> "TraceContext":

        return cls(trace_id=uuid4())
