from app.observability import (
    TraceContext,
)


def test_create_context():

    context = TraceContext.create()

    assert context.trace_id is not None
