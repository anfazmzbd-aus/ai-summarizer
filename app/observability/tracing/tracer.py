"""
Tracer abstraction.
"""

from __future__ import annotations

from .span import Span
from .trace_context import TraceContext


class Tracer:
    """
    Creates execution spans.
    """

    def start_span(
        self,
        name: str,
        context: TraceContext,
    ) -> Span:

        return Span(
            name=name,
            trace_id=context.trace_id,
        )

    def end_span(
        self,
        span: Span,
    ) -> None:

        span.end()
