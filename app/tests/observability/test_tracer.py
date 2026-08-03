from app.observability import (
    TraceContext,
    Tracer,
)


def test_start_end_span():

    tracer = Tracer()

    context = TraceContext.create()

    span = tracer.start_span(
        "worker.execute",
        context,
    )

    assert span.name == ("worker.execute")

    tracer.end_span(span)

    assert span.duration_ms is not None
