from app.observability.tracing import (
    OpenTelemetryTracer,
    TraceContext,
    configure_tracing,
    get_tracer,
)


def test_otel_span():

    configure_tracing(console_export=False)

    adapter = OpenTelemetryTracer(get_tracer())

    context = TraceContext.create()

    span = adapter.start_span(
        "worker.execute",
        context,
    )

    assert span is not None

    adapter.end_span(span)
