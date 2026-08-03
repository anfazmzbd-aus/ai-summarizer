"""
Prometheus text format formatter.
"""

from __future__ import annotations

from app.observability.metrics import (
    Counter,
    Gauge,
    Histogram,
    Metric,
)


class PrometheusFormatter:
    """
    Converts runtime metrics into Prometheus text format.
    """

    def format_metric(
        self,
        metric: Metric,
    ) -> str:

        name = self._normalize_name(metric.name)

        lines: list[str] = []

        if isinstance(metric, Counter):

            lines.append(f"{name}_total {metric.value}")

        elif isinstance(metric, Gauge):

            lines.append(f"{name} {metric.value}")

        elif isinstance(metric, Histogram):

            lines.append(f"{name}_count {metric.count}")

            lines.append(f"{name}_avg {metric.average}")

        return "\n".join(lines)

    def format_all(
        self,
        metrics: list[Metric],
    ) -> str:

        output = []

        for metric in metrics:

            output.append(self.format_metric(metric))

        return "\n".join(output)

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:

        return name.replace(
            ".",
            "_",
        )
