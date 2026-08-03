"""
Metrics registry.
"""

from __future__ import annotations

from typing import Iterable

from .counter import Counter
from .gauge import Gauge
from .histogram import Histogram
from .metric_base import Metric
from .snapshot import MetricSnapshot


class MetricsRegistry:

    def __init__(self) -> None:

        self._metrics: dict[str, Metric] = {}

    def register(
        self,
        metric: Metric,
    ) -> Metric:

        if metric.name in self._metrics:
            raise ValueError(f"Metric '{metric.name}' already exists.")

        self._metrics[metric.name] = metric

        return metric

    def get(
        self,
        name: str,
    ) -> Metric:

        return self._metrics[name]

    def contains(
        self,
        name: str,
    ) -> bool:

        return name in self._metrics

    def all(
        self,
    ) -> Iterable[Metric]:

        return self._metrics.values()

    def snapshot(
        self,
    ) -> list[MetricSnapshot]:

        snapshots: list[MetricSnapshot] = []

        for metric in self._metrics.values():

            if isinstance(metric, Counter):

                value = metric.value

            elif isinstance(metric, Gauge):

                value = metric.value

            elif isinstance(metric, Histogram):

                value = {
                    "count": metric.count,
                    "average": metric.average,
                }

            else:

                value = None

            snapshots.append(
                MetricSnapshot(
                    name=metric.name,
                    metric_type=metric.metric_type.value,
                    value=value,
                )
            )

        return snapshots
