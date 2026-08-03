from __future__ import annotations

from dataclasses import dataclass

from app.observability.tracing import TraceContext

from .observation import Observation


@dataclass(slots=True)
class ObservationContext:

    trace: TraceContext

    observation: Observation
