from app.orchestration.observability.execution_trace import (
    ExecutionTrace,
)


def test_trace():

    trace = ExecutionTrace()

    trace.record(
        "1",
        "summary",
        "started",
    )

    assert len(trace.export()) == 1
