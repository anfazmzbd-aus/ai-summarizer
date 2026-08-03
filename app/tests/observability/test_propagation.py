from app.observability.tracing import (
    TraceContext,
    inject_trace_context,
    extract_trace_context,
)


def test_trace_propagation():

    original = TraceContext.create()

    headers = inject_trace_context(original)

    restored = extract_trace_context(headers)

    assert original.trace_id == restored.trace_id
