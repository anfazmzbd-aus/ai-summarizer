"""V11 M1.3 application-path inventory architecture tests."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.core.application_paths import (
    CANONICAL_SUMMARIZATION_PATH,
    COMPATIBILITY_SUMMARIZATION_PATH,
    SUMMARIZATION_APPLICATION_PATHS,
    ApplicationPathRole,
)

ROOT = Path(__file__).resolve().parents[3]

CANONICAL_ROUTE = ROOT / "app" / "routes" / "ai.py"
COMPATIBILITY_ROUTE = ROOT / "app" / "api" / "v1" / "summarize_endpoint.py"


def test_exactly_one_canonical_summarization_path_exists() -> None:
    canonical = [
        path
        for path in SUMMARIZATION_APPLICATION_PATHS
        if path.role is ApplicationPathRole.CANONICAL
    ]

    assert len(canonical) == 1


def test_canonical_path_is_versioned_product_endpoint() -> None:
    assert CANONICAL_SUMMARIZATION_PATH.api_path == "/api/v1/summarize"
    assert CANONICAL_SUMMARIZATION_PATH.route_module == "app.routes.ai"
    assert (
        CANONICAL_SUMMARIZATION_PATH.composition_owner
        == "app.api.application.build_summarization_application"
    )


def test_legacy_endpoint_is_explicitly_compatibility_only() -> None:
    assert COMPATIBILITY_SUMMARIZATION_PATH.role is ApplicationPathRole.COMPATIBILITY
    assert COMPATIBILITY_SUMMARIZATION_PATH.api_path == "/summarize"
    assert not COMPATIBILITY_SUMMARIZATION_PATH.may_gain_product_behavior


def test_only_canonical_path_may_gain_v11_product_behavior() -> None:
    product_paths = [
        path
        for path in SUMMARIZATION_APPLICATION_PATHS
        if path.may_gain_product_behavior
    ]

    assert product_paths == [CANONICAL_SUMMARIZATION_PATH]


def test_canonical_route_uses_application_composition_boundary() -> None:
    source = CANONICAL_ROUTE.read_text(encoding="utf-8")

    assert "build_summarization_application" in source
    assert "build_summarization_service" not in source


def test_compatibility_route_does_not_import_v11_application_boundary() -> None:
    source = COMPATIBILITY_ROUTE.read_text(encoding="utf-8")

    assert "app.api.application" not in source
    assert "build_summarization_application" not in source


def test_paths_are_distinct() -> None:
    assert (
        CANONICAL_SUMMARIZATION_PATH.api_path
        != COMPATIBILITY_SUMMARIZATION_PATH.api_path
    )
    assert (
        CANONICAL_SUMMARIZATION_PATH.route_module
        != COMPATIBILITY_SUMMARIZATION_PATH.route_module
    )


def test_application_path_contract_is_immutable() -> None:
    with pytest.raises(FrozenInstanceError):
        CANONICAL_SUMMARIZATION_PATH.api_path = "/other"  # type: ignore[misc]
