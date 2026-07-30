from app.runtime.reporting.runtime_health import (
    RuntimeHealth,
)


def test_runtime_health_values():

    assert RuntimeHealth.HEALTHY.value == "healthy"

    assert RuntimeHealth.DEGRADED.value == "degraded"

    assert RuntimeHealth.FAILED.value == "failed"
