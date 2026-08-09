from typing import Any
from typing import Mapping

from app.orchestration.state.state_model import State


class StateBuilder:
    """
    Builds execution state.

    Runtime services are injected separately from execution data so that
    agents can access infrastructure capabilities without contaminating
    global_context.
    """

    @staticmethod
    def build(
        text: str,
        *,
        services: Mapping[str, Any] | None = None,
    ) -> State:
        """
        Build initial execution state.

        Parameters
        ----------
        text:
            Input text for the execution.

        services:
            Optional runtime capabilities available to agents.
        """

        return State(
            global_context={
                "text": text,
            },
            services=dict(services or {}),
        )
