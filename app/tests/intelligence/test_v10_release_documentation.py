"""Tests for V10 M10 release documentation baseline."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]

V10_DOCS = PROJECT_ROOT / "docs" / "v10"

README = V10_DOCS / "README.md"
ARCHITECTURE = V10_DOCS / "ARCHITECTURE.md"
RELEASE_BASELINE = V10_DOCS / "RELEASE_BASELINE.md"
V11_HANDOFF = V10_DOCS / "V11_HANDOFF.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v10_documentation_directory_exists() -> None:
    assert V10_DOCS.is_dir()


def test_required_v10_documents_exist() -> None:
    for path in (
        README,
        ARCHITECTURE,
        RELEASE_BASELINE,
        V11_HANDOFF,
    ):
        assert path.is_file()


def test_readme_identifies_v10() -> None:
    content = read(README)

    assert "AI Summarizer V10" in content
    assert "Bounded Intelligence Architecture" in content


def test_readme_declares_feature_freeze() -> None:
    content = read(README).lower()

    assert "feature-frozen" in content


def test_readme_contains_m1_through_m10() -> None:
    content = read(README)

    for milestone in (
        "M1",
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
        "M10",
    ):
        assert milestone in content


def test_architecture_contains_authority_mapping() -> None:
    content = read(ARCHITECTURE)

    assert "PRESERVE" in content
    assert "ADVISORY" in content
    assert "CONSTRAIN" in content
    assert "REVIEW" in content


def test_architecture_documents_rejected_handoff_rule() -> None:
    content = read(ARCHITECTURE).lower()

    assert "rejected directives cannot cross" in content


def test_architecture_contains_v10_invariants() -> None:
    content = read(ARCHITECTURE)

    assert "Canonical V10 Invariants" in content
    assert "Preserve cannot authorize execution change" in content
    assert "Observability does not create authority" in content


def test_release_baseline_targets_v10_release() -> None:
    content = read(RELEASE_BASELINE)

    assert "v10.0.0" in content


def test_release_baseline_contains_validation_commands() -> None:
    content = read(RELEASE_BASELINE)

    assert "pytest app/tests/intelligence -q" in content
    assert 'pytest -m "not live" -q' in content
    assert "pre-commit run --all-files" in content
    assert "git diff --check" in content


def test_release_baseline_does_not_claim_full_product_completion() -> None:
    content = read(RELEASE_BASELINE)

    assert (
        "full standalone application completion target " "remains `v12.0.0`" in content
    )


def test_v11_handoff_identifies_frontend_scope() -> None:
    content = read(V11_HANDOFF).lower()

    assert "frontend integration" in content
    assert "user text entry" in content


def test_v11_handoff_identifies_real_provider_scope() -> None:
    content = read(V11_HANDOFF).lower()

    assert "real-provider validation" in content


def test_v11_handoff_preserves_v10_invariants() -> None:
    content = read(V11_HANDOFF)

    assert "V11 Must Preserve" in content


def test_v11_handoff_identifies_v12_boundary() -> None:
    content = read(V11_HANDOFF)

    assert "V12 Boundary" in content
    assert "v12.0.0" in content


def test_documents_do_not_claim_v10_is_final_product_release() -> None:
    contents = "\n".join(
        read(path)
        for path in (
            README,
            ARCHITECTURE,
            RELEASE_BASELINE,
            V11_HANDOFF,
        )
    ).lower()

    forbidden = (
        "v10 is the final production-ready standalone release",
        "v10 completes the standalone application",
    )

    assert not any(phrase in contents for phrase in forbidden)
