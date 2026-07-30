from __future__ import annotations

from app.runtime.diagnostics.runtime_diagnostics import (
    RuntimeDiagnostics,
)

from app.runtime.observability.runtime_snapshot import (
    RuntimeSnapshot,
)


class ExecutionAnalyzer:
    """
    Performs runtime execution analysis.
    """

    def analyze(
        self,
        snapshot: RuntimeSnapshot,
    ) -> RuntimeDiagnostics:

        diagnostics = RuntimeDiagnostics()

        metrics = snapshot.metrics

        if metrics.failed_nodes > 0:
            diagnostics.healthy = False

            diagnostics.issues.append("Execution contains failed nodes.")

        return diagnostics
