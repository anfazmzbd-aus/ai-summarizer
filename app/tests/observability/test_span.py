from app.observability import (
    Span,
    TraceContext,
)


def test_span_lifecycle():

    context = TraceContext.create()

    span = Span(
        name="execution",
        trace_id=context.trace_id,
    )

    assert span.ended_at is None

    span.end()

    assert span.ended_at is not None
