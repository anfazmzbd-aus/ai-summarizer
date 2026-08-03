"""
Shared observability container.
"""

from __future__ import annotations

from app.observability.metrics import (
    MetricsRegistry,
    RuntimeMetrics,
)
from app.observability.prometheus import (
    PrometheusExporter,
)


class ObservabilityContainer:

    def __init__(self) -> None:

        self.metrics_registry = MetricsRegistry()

        self.runtime_metrics = RuntimeMetrics(self.metrics_registry)

        self.prometheus_exporter = PrometheusExporter(self.metrics_registry)
