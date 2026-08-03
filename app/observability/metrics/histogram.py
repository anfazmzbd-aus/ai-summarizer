from __future__ import annotations

from statistics import mean
from threading import Lock

from .metric_base import Metric
from .metric_types import MetricType


class Histogram(Metric):

    def __init__(
        self,
        name: str,
        description: str = "",
    ) -> None:

        super().__init__(
            name=name,
            metric_type=MetricType.HISTOGRAM,
            description=description,
        )

        self._values: list[float] = []

        self._lock = Lock()

    def observe(
        self,
        value: float,
    ) -> None:

        with self._lock:
            self._values.append(value)

    @property
    def count(self) -> int:

        return len(self._values)

    @property
    def average(self) -> float:

        if not self._values:
            return 0.0

        return mean(self._values)

    @property
    def values(self) -> list[float]:

        return list(self._values)
