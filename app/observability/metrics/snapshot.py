"""
Metric snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True, frozen=True)
class MetricSnapshot:

    name: str

    metric_type: str

    value: Any
