from app.observability.container import (
    ObservabilityContainer,
)


def test_container():

    container = ObservabilityContainer()

    assert container.metrics_registry is not None

    assert container.runtime_metrics is not None

    assert container.prometheus_exporter is not None
