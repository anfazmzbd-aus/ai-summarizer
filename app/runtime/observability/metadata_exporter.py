from __future__ import annotations

from dataclasses import asdict

from app.runtime.observability.runtime_snapshot import RuntimeSnapshot


class MetadataExporter:
    """
    Converts runtime snapshots into
    serializable structures.
    """

    def export(
        self,
        snapshot: RuntimeSnapshot,
    ) -> dict[str, object]:
        return asdict(snapshot)
