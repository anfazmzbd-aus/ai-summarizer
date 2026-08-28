"""
Architecture tests for the canonical API application boundary.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ROUTE_FILE = ROOT / "app" / "routes" / "ai.py"
APPLICATION_FILE = ROOT / "app" / "api" / "application.py"
ROUTE = ROOT / "app" / "routes" / "ai.py"
APPLICATION = ROOT / "app" / "api" / "application.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_route_uses_canonical_application_builder() -> None:
    content = read(ROUTE)

    assert "build_summarization_application" in content
    assert "build_summarization_service" not in content


def test_canonical_application_owns_service_construction() -> None:
    content = read(APPLICATION)

    assert "build_summarization_service" in content
    assert "SummarizationApplication" in content


def test_route_does_not_construct_summarization_service_directly():
    source = ROUTE_FILE.read_text(encoding="utf-8")

    assert "build_summarization_service" not in source
    assert "SummarizationService(" not in source


def test_application_boundary_composes_pipeline_and_intelligence_adapters():
    source = APPLICATION_FILE.read_text(encoding="utf-8")

    assert "app.core.intelligence_integration" in source
    assert "app.intelligence" not in source
    assert "app.providers" not in source
    assert "app.runtime" not in source
    assert "app.orchestration" not in source


def test_route_does_not_depend_on_internal_ai_request_contract() -> None:
    content = read(ROUTE)

    assert "app.ai" not in content
    assert "SummarizationRequest" not in content
    assert "SummarizationApplicationRequest" in content
