from datetime import datetime, timedelta, timezone

from app.runtime.runtime_metadata import (
    RuntimeMetadata,
    RuntimeStatus,
)


def test_default_metadata() -> None:
    metadata = RuntimeMetadata()

    assert metadata.status == RuntimeStatus.NEW
    assert metadata.started_at is None
    assert metadata.completed_at is None
    assert metadata.duration_seconds is None


def test_duration_calculation() -> None:
    metadata = RuntimeMetadata()

    metadata.started_at = datetime.now(timezone.utc)
    metadata.completed_at = metadata.started_at + timedelta(seconds=5)

    assert metadata.duration_seconds == 5.0


def test_execution_id_exists() -> None:
    metadata = RuntimeMetadata()

    assert metadata.execution_id is not None
