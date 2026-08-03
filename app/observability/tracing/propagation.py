"""
Trace propagation helpers.
"""

from __future__ import annotations

from uuid import UUID

from .trace_context import TraceContext


def inject_trace_context(
    context: TraceContext,
) -> dict[str, str]:

    return {"trace_id": str(context.trace_id)}


def extract_trace_context(
    headers: dict[str, str],
) -> TraceContext:

    return TraceContext(trace_id=UUID(headers["trace_id"]))
