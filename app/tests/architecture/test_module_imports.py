"""
Architecture smoke tests for runtime modules.

These tests verify that runtime modules can be imported without
raising ImportError, circular import errors, or import-time
initialization failures.
"""

from __future__ import annotations

import importlib

import pytest

MODULES = [
    "app.runtime.cache",
    "app.runtime.checkpoint",
    "app.runtime.diagnostics",
    "app.runtime.events",
    "app.runtime.hooks",
    "app.runtime.intelligence",
    "app.runtime.middleware",
    "app.runtime.observability",
    "app.runtime.persistence",
    "app.runtime.policy",
    "app.runtime.reporting",
    "app.runtime.runtime_context",
    "app.runtime.runtime_manager",
    "app.runtime.runtime_metadata",
    "app.runtime.runtime_session",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_runtime_module_imports(module_name: str) -> None:
    """Every runtime module should import successfully."""
    module = importlib.import_module(module_name)

    assert module is not None
