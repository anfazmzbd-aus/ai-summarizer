from app.observability.metrics import (
    Counter,
    MetricsRegistry,
)

from app.observability.prometheus import (
    PrometheusExporter,
)


def test_exporter():

    registry = MetricsRegistry()

    counter = registry.register(Counter("runtime.tasks.submitted"))

    counter.increment(10)

    exporter = PrometheusExporter(registry)

    output = exporter.export()

    assert "runtime_tasks_submitted_total 10" in output
