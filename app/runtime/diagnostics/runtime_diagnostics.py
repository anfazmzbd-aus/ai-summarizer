from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeDiagnostics:
    """
    Diagnostic result for one runtime execution.
    """

    healthy: bool = True

    issues: list[str] = field(default_factory=list)

    warnings: list[str] = field(default_factory=list)

    statistics: dict[str, object] = field(default_factory=dict)

    failures: list[str] = field(default_factory=list)
