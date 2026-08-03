from __future__ import annotations

from threading import Lock

from .metric_base import Metric
from .metric_types import MetricType


class Gauge(Metric):

    def __init__(
        self,
        name: str,
        description: str = "",
    ) -> None:

        super().__init__(
            name=name,
            metric_type=MetricType.GAUGE,
            description=description,
        )

        self._value = 0.0

        self._lock = Lock()

    def set(
        self,
        value: float,
    ) -> None:

        with self._lock:
            self._value = value

    def increment(
        self,
        value: float = 1,
    ) -> None:

        with self._lock:
            self._value += value

    def decrement(
        self,
        value: float = 1,
    ) -> None:

        with self._lock:
            self._value -= value

    @property
    def value(self) -> float:

        with self._lock:
            return self._value
