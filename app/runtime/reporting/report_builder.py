from __future__ import annotations

from app.runtime.diagnostics.runtime_diagnostics import RuntimeDiagnostics
from app.runtime.observability.runtime_snapshot import RuntimeSnapshot
from app.runtime.reporting.execution_summary import ExecutionSummary
from app.runtime.reporting.runtime_health import RuntimeHealth
from app.runtime.reporting.runtime_report import RuntimeReport


class ReportBuilder:
    """
    Builds runtime reports from runtime state.
    """

    def build_report(
        self,
        snapshot: RuntimeSnapshot,
        diagnostics: RuntimeDiagnostics,
    ) -> RuntimeReport:

        metrics = snapshot.metrics

        status = (
            RuntimeHealth.HEALTHY.value
            if diagnostics.healthy
            else RuntimeHealth.FAILED.value
        )

        return RuntimeReport(
            status=status,
            execution_time_seconds=metrics.execution_time_seconds,
            total_layers=metrics.total_layers,
            completed_layers=metrics.completed_layers,
            failed_nodes=metrics.failed_nodes,
            healthy=diagnostics.healthy,
            issues=list(diagnostics.issues),
            warnings=list(diagnostics.warnings),
        )

    def build_summary(
        self,
        snapshot: RuntimeSnapshot,
        diagnostics: RuntimeDiagnostics,
    ) -> ExecutionSummary:

        metrics = snapshot.metrics

        completion_rate = 0.0

        if metrics.total_layers:
            completion_rate = metrics.completed_layers / metrics.total_layers

        status = (
            RuntimeHealth.HEALTHY.value
            if diagnostics.healthy
            else RuntimeHealth.FAILED.value
        )

        return ExecutionSummary(
            status=status,
            completion_rate=completion_rate,
            execution_time_seconds=metrics.execution_time_seconds,
            healthy=diagnostics.healthy,
        )
