from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ObserverContext:
    """
    Carries runtime observation data for a single execution.
    """

    execution_id: str

    current_layer: int | None = None

    current_node: str | None = None

    observations: list[str] = field(default_factory=list)

    def record(
        self,
        message: str,
    ) -> None:
        self.observations.append(message)
