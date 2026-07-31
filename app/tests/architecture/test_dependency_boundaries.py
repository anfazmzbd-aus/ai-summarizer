"""
Architecture dependency boundary tests.

These tests enforce the intended dependency direction between
major runtime components and help prevent architectural drift.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


FORBIDDEN_IMPORTS = {
    "app/runtime/reporting": ("app.orchestration.execution",),
    "app/runtime/diagnostics": ("app.runtime.runtime_manager",),
    "app/runtime/observability": ("app.orchestration.scheduler",),
}


def iter_python_files(package: str):
    package_path = ROOT / package.replace(".", "/")

    if not package_path.exists():
        return []

    return package_path.rglob("*.py")


def imported_modules(file_path: Path):
    tree = ast.parse(file_path.read_text(encoding="utf-8"))

    modules = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)

    return modules


def test_dependency_boundaries():
    violations = []

    for package, forbidden in FORBIDDEN_IMPORTS.items():

        for py_file in iter_python_files(package):

            imports = imported_modules(py_file)

            for imported in imports:

                if any(imported.startswith(item) for item in forbidden):

                    violations.append(f"{py_file.relative_to(ROOT)} imports {imported}")

    assert not violations, "\n".join(violations)
