"""
AI Summarizer V7.8 Runtime Session

Owns all runtime-scoped objects for a single execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.orchestration.execution.execution_context import ExecutionContext
from app.orchestration.graph.graph_schema import ExecutionGraph
from app.runtime.cancellation_token import CancellationToken
from app.runtime.intelligence.decision import Decision
from app.runtime.runtime_config import RuntimeConfig
from app.runtime.runtime_context import RuntimeContext
from app.runtime.runtime_metadata import RuntimeMetadata
from app.runtime.observability.execution_metrics import ExecutionMetrics
from app.runtime.observability.execution_timeline import ExecutionTimeline
from app.runtime.observability.runtime_snapshot import RuntimeSnapshot
from app.runtime.diagnostics.execution_analyzer import (
    ExecutionAnalyzer,
)

from app.runtime.diagnostics.execution_statistics import (
    ExecutionStatistics,
)

from app.runtime.diagnostics.runtime_diagnostics import (
    RuntimeDiagnostics,
)
from app.runtime.reporting.report_builder import ReportBuilder
from app.runtime.reporting.runtime_report import RuntimeReport


@dataclass(slots=True)
class RuntimeSession:
    """
    Represents one runtime execution.

    Aggregates every runtime-scoped object.
    """

    config: RuntimeConfig = field(default_factory=RuntimeConfig)

    metadata: RuntimeMetadata = field(default_factory=RuntimeMetadata)

    cancellation_token: CancellationToken = field(default_factory=CancellationToken)

    execution_context: ExecutionContext = field(default_factory=ExecutionContext)

    runtime_context: RuntimeContext = field(init=False)

    #
    # V7.9 Phase 2 additions
    #

    execution_graph: ExecutionGraph | None = None

    decision: Decision | None = None

    execution_result: object | None = None

    snapshot: RuntimeSnapshot = field(init=False)

    diagnostics: RuntimeDiagnostics = field(init=False)

    report: RuntimeReport | None = field(
        init=False,
        default=None,
    )

    def __post_init__(self) -> None:
        self.runtime_context = RuntimeContext(
            execution_context=self.execution_context,
            config=self.config,
            metadata=self.metadata,
            cancellation_token=self.cancellation_token,
        )
        self.snapshot = RuntimeSnapshot(
            metrics=ExecutionMetrics(),
            timeline=ExecutionTimeline(),
        )

        # Wire observability here
        self.metadata.observability = self.snapshot

        self.diagnostics = RuntimeDiagnostics()

        self.metadata.diagnostics = self.diagnostics

    def analyze_execution(
        self,
    ) -> None:
        """
        Analyze runtime execution snapshot.
        """

        analyzer = ExecutionAnalyzer()

        statistics = ExecutionStatistics()

        self.diagnostics = analyzer.analyze(
            self.snapshot,
        )

        self.diagnostics.statistics = statistics.calculate(
            self.snapshot,
        )

    def build_report(self) -> None:
        """
        Builds the runtime execution report.
        """

        builder = ReportBuilder()

        self.report = builder.build_report(
            self.snapshot,
            self.diagnostics,
        )

        self.metadata.report = self.report
