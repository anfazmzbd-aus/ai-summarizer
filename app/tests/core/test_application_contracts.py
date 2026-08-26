"""Tests for V11 application-level contracts."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from app.core.application_contracts import (
    SummarizationApplicationRequest,
    SummarizationApplicationResult,
)


def test_application_request_preserves_product_input() -> None:
    request = SummarizationApplicationRequest(
        text="Source text",
        provider="fake",
        model="demo",
        prompt_name="summary",
    )

    assert request.text == "Source text"
    assert request.provider == "fake"
    assert request.model == "demo"
    assert request.prompt_name == "summary"


def test_application_request_supports_optional_provider_settings() -> None:
    request = SummarizationApplicationRequest(
        text="Source text",
    )

    assert request.provider is None
    assert request.model is None
    assert request.prompt_name is None


def test_application_result_calculates_total_tokens() -> None:
    result = SummarizationApplicationResult(
        summary="summary",
        model="demo",
        prompt_tokens=10,
        completion_tokens=5,
    )

    assert result.total_tokens == 15


def test_application_request_is_immutable() -> None:
    request = SummarizationApplicationRequest(
        text="Source text",
    )

    with pytest.raises(FrozenInstanceError):
        request.text = "changed"  # type: ignore[misc]


def test_application_result_is_immutable() -> None:
    result = SummarizationApplicationResult(
        summary="summary",
        model="demo",
        prompt_tokens=10,
        completion_tokens=5,
    )

    with pytest.raises(FrozenInstanceError):
        result.summary = "changed"  # type: ignore[misc]


def test_application_result_has_read_only_metadata_default() -> None:
    result = SummarizationApplicationResult(
        summary="summary",
        model="demo",
        prompt_tokens=10,
        completion_tokens=5,
    )

    assert result.metadata.strategy is None
    assert result.metadata.chunk_count is None
    assert dict(result.metadata.attributes) == {}
