"""Tests for V11 read-only integration metadata."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.core.application_metadata import (
    SummarizationExecutionMetadata,
)


def test_metadata_defaults_are_non_authoritative() -> None:
    metadata = SummarizationExecutionMetadata()

    assert metadata.strategy is None
    assert metadata.chunk_count is None
    assert metadata.intelligence_mode is None
    assert metadata.trace_id is None
    assert metadata.explainability_summary is None
    assert dict(metadata.attributes) == {}


def test_metadata_accepts_descriptive_values() -> None:
    metadata = SummarizationExecutionMetadata(
        strategy="direct",
        chunk_count=1,
        intelligence_mode="preserve",
        trace_id="trace-123",
        explainability_summary="Existing execution preserved.",
    )

    assert metadata.strategy == "direct"
    assert metadata.chunk_count == 1
    assert metadata.intelligence_mode == "preserve"
    assert metadata.trace_id == "trace-123"


def test_metadata_is_immutable() -> None:
    metadata = SummarizationExecutionMetadata()

    with pytest.raises(FrozenInstanceError):
        metadata.strategy = "map_reduce"  # type: ignore[misc]


def test_metadata_attributes_are_read_only() -> None:
    metadata = SummarizationExecutionMetadata(
        attributes={"source": "application"},
    )

    with pytest.raises(TypeError):
        metadata.attributes["source"] = "changed"  # type: ignore[index]


def test_metadata_copies_input_attributes() -> None:
    attributes = {"source": "application"}

    metadata = SummarizationExecutionMetadata(
        attributes=attributes,
    )

    attributes["source"] = "changed"

    assert metadata.attributes["source"] == "application"
