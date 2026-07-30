from app.runtime.diagnostics.runtime_diagnostics import (
    RuntimeDiagnostics,
)


def test_runtime_diagnostics_defaults():
    diagnostics = RuntimeDiagnostics()

    assert diagnostics.healthy is True
    assert diagnostics.issues == []
    assert diagnostics.warnings == []
    assert diagnostics.statistics == {}
    assert diagnostics.failures == []


def test_runtime_diagnostics_failure_state():
    diagnostics = RuntimeDiagnostics()

    diagnostics.healthy = False
    diagnostics.failures.append(
        "TimeoutError",
    )

    assert diagnostics.healthy is False
    assert diagnostics.failures == [
        "TimeoutError",
    ]
