"""
Prometheus exporter.
"""

from __future__ import annotations

from app.observability.metrics import (
    MetricsRegistry,
)

from .formatter import PrometheusFormatter


class PrometheusExporter:

    def __init__(
        self,
        registry: MetricsRegistry,
    ) -> None:

        self.registry = registry

        self.formatter = PrometheusFormatter()

    def export(
        self,
    ) -> str:

        return self.formatter.format_all(list(self.registry.all()))
