from __future__ import annotations

import zipfile
from pathlib import Path

from scripts.build_release_artifact import (
    build,
    calculate_sha256,
    should_include,
)


def test_release_excludes_runtime_log():
    assert should_include("logs/agent_system.log") is False


def test_release_excludes_tests():
    assert should_include("app/tests/api/test_application.py") is False


def test_release_excludes_legacy_application():
    assert should_include("app/legacy/v7.6/main.py") is False


def test_release_excludes_runtime_database():
    assert should_include("summaries.db") is False


def test_release_excludes_development_requirements():
    assert should_include("requirements-dev.txt") is False
    assert should_include("requirements_test.txt") is False
    assert should_include("requirements_now.txt") is False
    assert should_include("requirements_f.txt") is False


def test_release_excludes_development_tooling():
    assert should_include("pyproject.toml") is False
    assert should_include(".pre-commit-config.yaml") is False
    assert should_include("Makefile") is False
    assert should_include("AGENTS.md") is False
    assert should_include("CODEX_FIRST_PROMPT.txt") is False
    assert should_include("freeze_test.txt") is False
    assert should_include("tools.py") is False


def test_release_excludes_development_github_configuration():
    assert should_include(".github/workflows/ci.yml") is False


def test_release_excludes_historical_documentation():
    assert should_include("docs/v11/ARCHITECTURE_INDEX.md") is False
    assert should_include("docs/V9/V9.0.1_PROVIDER_FRAMEWORK.md") is False
    assert should_include("docs/releases/V8.0.0.md") is False
    assert should_include("docs/DECISIONS/TESTING.md") is False


def test_release_includes_application_source():
    assert should_include("app/main.py") is True
    assert should_include("app/api/application.py") is True


def test_release_includes_static_assets():
    assert should_include("static/app.js") is True
    assert should_include("static/style.css") is True


def test_release_includes_runtime_requirements():
    assert should_include("requirements.txt") is True


def test_release_includes_environment_example():
    assert should_include(".env.example") is True


def test_release_includes_product_documentation():
    assert should_include("README.md") is True
    assert should_include("CHANGELOG.md") is True
    assert should_include("docs/v12/V12_GOVERNANCE.md") is True
    assert should_include("docs/v12/INSTALLATION.md") is True
    assert should_include("docs/v12/CONFIGURATION.md") is True
    assert should_include("docs/v12/OPERATIONS.md") is True
    assert should_include("docs/v12/TROUBLESHOOTING.md") is True
    assert should_include("docs/v12/RELEASE_NOTES.md") is True


def test_release_includes_release_and_runtime_scripts():
    assert should_include("scripts/build_release_artifact.py") is True
    assert should_include("scripts/validate_runtime.py") is True


def test_unrecognized_tracked_file_is_excluded_by_default():
    assert should_include("unexpected-development-file.txt") is False
    assert should_include("scripts/random_developer_script.py") is False
    assert should_include("docs/random-history.md") is False


def test_built_artifact_enforces_release_boundary(
    tmp_path: Path,
):
    artifact_path, checksum_path = build(
        version="12.0.0-test",
        output_directory=tmp_path,
    )

    prefix = "ai-summarizer-v12.0.0-test/"

    with zipfile.ZipFile(artifact_path) as archive:
        names = set(archive.namelist())

    assert f"{prefix}README.md" in names
    assert f"{prefix}CHANGELOG.md" in names
    assert f"{prefix}.env.example" in names
    assert f"{prefix}requirements.txt" in names
    assert f"{prefix}app/main.py" in names
    assert f"{prefix}static/app.js" in names
    assert f"{prefix}docs/v12/V12_GOVERNANCE.md" in names

    assert f"{prefix}summaries.db" not in names
    assert f"{prefix}requirements-dev.txt" not in names
    assert f"{prefix}pyproject.toml" not in names
    assert f"{prefix}Makefile" not in names

    assert not any(name.startswith(f"{prefix}app/tests/") for name in names)
    assert not any(name.startswith(f"{prefix}app/legacy/") for name in names)
    assert not any(name.startswith(f"{prefix}docs/v11/") for name in names)
    assert not any(name.startswith(f"{prefix}docs/V9/") for name in names)
    assert not any(name.startswith(f"{prefix}docs/releases/") for name in names)

    expected_checksum = calculate_sha256(artifact_path)

    checksum_text = checksum_path.read_text(encoding="utf-8")

    assert checksum_text == (f"{expected_checksum}  {artifact_path.name}\n")


def test_release_build_is_reproducible(
    tmp_path: Path,
):
    first_directory = tmp_path / "first"
    second_directory = tmp_path / "second"

    first_artifact, _ = build(
        version="12.0.0-test",
        output_directory=first_directory,
    )
    second_artifact, _ = build(
        version="12.0.0-test",
        output_directory=second_directory,
    )

    assert first_artifact.read_bytes() == second_artifact.read_bytes()
    assert calculate_sha256(first_artifact) == calculate_sha256(second_artifact)
