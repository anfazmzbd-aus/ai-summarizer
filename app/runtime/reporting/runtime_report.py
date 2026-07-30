from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeReport:
    """
    Immutable runtime execution report.
    """

    status: str

    execution_time_seconds: float

    total_layers: int

    completed_layers: int

    failed_nodes: int

    healthy: bool

    issues: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)
