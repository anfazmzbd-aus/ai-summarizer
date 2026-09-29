"""V13 M9.2 release identity certification."""

from pathlib import Path

from app.version import __version__


PROJECT_ROOT = Path(__file__).resolve().parents[3]

VERSION_FILE = PROJECT_ROOT / "app" / "version.py"
INDEX_HTML = PROJECT_ROOT / "app" / "templates" / "index.html"
ARTIFACT_BUILDER = PROJECT_ROOT / "scripts" / "build_release_artifact.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_application_release_candidate_identity():
    assert __version__ == "13.0.0-rc1"


def test_version_module_contains_release_candidate_identity():
    content = read(VERSION_FILE)

    assert '__version__ = "13.0.0-rc1"' in content


def test_version_module_has_no_active_v12_identity():
    content = read(VERSION_FILE)

    assert '__version__ = "12.0.0"' not in content


def test_frontend_identifies_major_version_13():
    html = read(INDEX_HTML)

    assert 'aria-label="Application version 13"' in html


def test_release_builder_is_version_parameterized():
    source = read(ARTIFACT_BUILDER)

    assert "def build(version: str" in source
    assert 'f"ai-summarizer-v{version}.zip"' in source


def test_release_builder_uses_version_rooted_archive():
    source = read(ARTIFACT_BUILDER)

    assert 'f"ai-summarizer-v{version}/{relative_path}"' in source


def test_release_builder_requires_version_argument():
    source = read(ARTIFACT_BUILDER)

    assert '"--version"' in source


def test_release_candidate_identity_is_not_final_release_identity():
    assert __version__ != "13.0.0"


def test_release_identity_has_no_milestone_suffix():
    assert "-m" not in __version__


def test_release_candidate_uses_rc1_suffix():
    assert __version__.endswith("-rc1")
