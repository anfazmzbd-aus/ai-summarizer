"""V11 M1.5 metadata-boundary architecture tests."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

METADATA = ROOT / "app" / "core" / "application_metadata.py"
CONTRACTS = ROOT / "app" / "core" / "application_contracts.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_metadata_contract_does_not_import_v9_domain_objects() -> None:
    content = read(METADATA)

    assert "app.summarization" not in content


def test_metadata_contract_does_not_import_v10_intelligence_objects() -> None:
    content = read(METADATA)

    assert "app.intelligence" not in content


def test_metadata_contract_does_not_import_runtime_or_provider_objects() -> None:
    content = read(METADATA)

    assert "app.runtime" not in content
    assert "app.orchestration" not in content
    assert "app.providers" not in content


def test_application_contract_uses_metadata_as_read_only_product_contract() -> None:
    content = read(CONTRACTS)

    assert "SummarizationExecutionMetadata" in content
