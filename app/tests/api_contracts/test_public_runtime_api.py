"""
Public runtime API contract tests.

These tests protect the public API surface from accidental
breaking changes.
"""

from __future__ import annotations

import inspect

from app.orchestration.execution.execution_engine import ExecutionEngine
from app.runtime.runtime_manager import RuntimeManager

try:
    from app.runtime.intelligence.decision_engine import DecisionEngine
except ImportError:
    DecisionEngine = None

try:
    from app.runtime.reporting.report_builder import ReportBuilder
except ImportError:
    ReportBuilder = None


def parameter_names(callable_obj):
    return list(inspect.signature(callable_obj).parameters)


def test_runtime_manager_run_signature():
    assert parameter_names(RuntimeManager.run) == [
        "self",
        "text",
        "contracts",
        "state",
    ]


def test_execution_engine_execute_signature():
    assert parameter_names(ExecutionEngine.execute) == [
        "self",
        "graph",
        "initial_state",
        "decision",
    ]


def test_decision_engine_signature():
    if DecisionEngine is None:
        return

    assert parameter_names(DecisionEngine.decide) == [
        "self",
        "execution_context",
    ]


def test_report_builder_signature():
    if ReportBuilder is None:
        return

    assert parameter_names(ReportBuilder.build_report) == [
        "self",
        "snapshot",
        "diagnostics",
    ]
