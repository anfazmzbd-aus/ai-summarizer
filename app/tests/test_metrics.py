from app.orchestration.observability.metrics import (
    RuntimeMetrics,
)


def test_metrics():

    m = RuntimeMetrics()

    m.increment("nodes")

    assert m.export()["nodes"] == 1
