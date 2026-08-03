from app.observability.context import (
    Observation,
    ObservationContext,
)

from app.observability import TraceContext


def test_context():

    context = ObservationContext(
        trace=TraceContext.create(),
        observation=Observation(),
    )

    assert context.trace is not None
