"""
OpenTelemetry tracer adapter.

Keeps V8 runtime independent
from OpenTelemetry internals.
"""

from __future__ import annotations

from .trace_context import TraceContext


class OpenTelemetryTracer:

    def __init__(
        self,
        tracer,
    ) -> None:

        self._tracer = tracer

    def start_span(
        self,
        name: str,
        context: TraceContext,
    ):

        span = self._tracer.start_span(name)

        span.set_attribute(
            "execution.trace_id",
            str(context.trace_id),
        )

        return span

    def end_span(
        self,
        span,
    ) -> None:

        span.end()
