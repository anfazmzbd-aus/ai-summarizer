"""
Architecture smoke tests for runtime modules.

These tests verify that runtime modules can be imported without
raising ImportError, circular import errors, or import-time
initialization failures.
"""

from __future__ import annotations

import importlib
import pkgutil

import app.runtime


def test_all_runtime_modules_import() -> None:
    package = app.runtime

    for module_info in pkgutil.walk_packages(
        package.__path__,
        package.__name__ + ".",
    ):
        module = importlib.import_module(module_info.name)

        assert module is not None
