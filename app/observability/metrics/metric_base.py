"""
Base metric class.
"""

from __future__ import annotations

from abc import ABC

from .metric_types import MetricType


class Metric(ABC):

    def __init__(
        self,
        name: str,
        metric_type: MetricType,
        description: str = "",
    ) -> None:

        self._name = name
        self._type = metric_type
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def metric_type(self) -> MetricType:
        return self._type

    @property
    def description(self) -> str:
        return self._description
