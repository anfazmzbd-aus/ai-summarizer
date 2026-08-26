"""V11 M1.1 canonical application integration architecture tests."""

from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from app.core.application_integration import (
    V11_APPLICATION_INTEGRATION_BOUNDARY,
)

ROOT = Path(__file__).resolve().parents[3]


def _imported_modules(file_path: Path) -> list[str]:
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    modules: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)

    return modules


def test_canonical_product_api_is_versioned_and_distinct_from_compatibility() -> None:
    boundary = V11_APPLICATION_INTEGRATION_BOUNDARY

    assert boundary.canonical_api_path == "/api/v1/summarize"
    assert boundary.compatibility_api_path == "/summarize"
    assert boundary.canonical_api_path != boundary.compatibility_api_path


def test_canonical_route_and_application_service_are_single_named_owners() -> None:
    boundary = V11_APPLICATION_INTEGRATION_BOUNDARY

    assert boundary.canonical_route_module == "app.routes.ai"
    assert (
        boundary.application_service_owner
        == "app.api.application.build_summarization_application"
    )


def test_v9_pipeline_remains_summarization_owner() -> None:
    assert (
        V11_APPLICATION_INTEGRATION_BOUNDARY.summarization_pipeline_owner
        == "app.summarization.pipeline.SummarizationPipeline"
    )


def test_v10_intelligence_precedes_existing_execution_and_provider_runtime() -> None:
    boundary = V11_APPLICATION_INTEGRATION_BOUNDARY
    flow = boundary.canonical_flow

    intelligence_index = flow.index("app.intelligence")
    orchestration_index = flow.index("app.orchestration")
    runtime_index = flow.index("app.runtime")
    provider_index = flow.index("app.providers.runtime.ProviderRuntime")

    assert intelligence_index < orchestration_index
    assert intelligence_index < runtime_index
    assert runtime_index < provider_index


def test_v7_v8_execution_runtime_owners_are_preserved() -> None:
    assert V11_APPLICATION_INTEGRATION_BOUNDARY.execution_runtime_owners == (
        "app.orchestration",
        "app.runtime",
        "app.distributed",
    )


def test_v10_intelligence_does_not_import_provider_or_execution_implementations() -> (
    None
):
    forbidden_prefixes = (
        "app.providers",
        "app.ai.providers",
        "app.orchestration.execution",
        "app.runtime.runtime_manager",
    )
    violations: list[str] = []

    for file_path in (ROOT / "app" / "intelligence").glob("*.py"):
        for imported in _imported_modules(file_path):
            if imported.startswith(forbidden_prefixes):
                violations.append(f"{file_path.relative_to(ROOT)} imports {imported}")

    assert not violations, "\n".join(violations)


def test_integration_boundary_is_immutable() -> None:
    boundary = V11_APPLICATION_INTEGRATION_BOUNDARY

    with pytest.raises(FrozenInstanceError):
        boundary.canonical_api_path = "/other"  # type: ignore[misc]


def test_canonical_application_facade_is_explicit():
    assert (
        V11_APPLICATION_INTEGRATION_BOUNDARY.application_facade_owner
        == "app.api.application.SummarizationApplication"
    )
