from __future__ import annotations

from threading import Lock

from .metric_base import Metric
from .metric_types import MetricType


class Counter(Metric):

    def __init__(
        self,
        name: str,
        description: str = "",
    ) -> None:

        super().__init__(
            name=name,
            metric_type=MetricType.COUNTER,
            description=description,
        )

        self._value = 0

        self._lock = Lock()

    def increment(
        self,
        value: int = 1,
    ) -> None:

        with self._lock:
            self._value += value

    @property
    def value(self) -> int:

        with self._lock:
            return self._value
