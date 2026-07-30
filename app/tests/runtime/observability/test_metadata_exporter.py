from app.runtime.observability.execution_metrics import (
    ExecutionMetrics,
)
from app.runtime.observability.execution_timeline import (
    ExecutionTimeline,
)
from app.runtime.observability.metadata_exporter import (
    MetadataExporter,
)
from app.runtime.observability.runtime_snapshot import (
    RuntimeSnapshot,
)


def test_export_snapshot():
    snapshot = RuntimeSnapshot(
        metrics=ExecutionMetrics(),
        timeline=ExecutionTimeline(),
    )

    exporter = MetadataExporter()

    exported = exporter.export(snapshot)

    assert isinstance(
        exported,
        dict,
    )

    assert "metrics" in exported

    assert "timeline" in exported
