"""M3 architecture certification guards."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
M3_FILES = (
    ROOT / "app" / "api" / "application.py",
    ROOT / "app" / "core" / "intelligence_integration.py",
    ROOT / "app" / "core" / "execution_feedback_integration.py",
)


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_m3_application_and_feedback_layers_preserve_ownership() -> None:
    application_imports = imported_modules(M3_FILES[0])
    feedback_imports = imported_modules(M3_FILES[2])

    assert not any(
        module.startswith(("app.intelligence", "app.providers", "app.runtime"))
        for module in application_imports
    )
    assert not any(
        module.startswith(
            (
                "app.providers",
                "app.runtime",
                "app.orchestration",
                "app.summarization.pipeline",
            )
        )
        for module in feedback_imports
    )


def test_m3_intelligence_projection_does_not_depend_on_execution_owners() -> None:
    imports = imported_modules(M3_FILES[1])

    assert not any(
        module.startswith(
            (
                "app.providers",
                "app.runtime",
                "app.orchestration",
                "app.summarization.pipeline",
            )
        )
        for module in imports
    )
