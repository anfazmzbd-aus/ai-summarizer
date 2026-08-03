from __future__ import annotations

from .observation import Observation
from .observation_context import ObservationContext
from app.observability.tracing import TraceContext


class ObservationManager:

    def create(self) -> ObservationContext:

        return ObservationContext(
            trace=TraceContext.create(),
            observation=Observation(),
        )

    def finish(
        self,
        context: ObservationContext,
    ) -> None:

        context.observation.finish()
