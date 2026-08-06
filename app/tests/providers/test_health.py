from app.providers.health import (
    ProviderHealth,
    ProviderStatus,
)


def test_healthy_factory():
    health = ProviderHealth.healthy(
        provider="mock",
        latency_ms=12.5,
    )

    assert health.provider == "mock"
    assert health.status is ProviderStatus.HEALTHY
    assert health.latency_ms == 12.5
    assert health.error is None


def test_unavailable_factory():
    health = ProviderHealth.unavailable(
        provider="mock",
        error="connection failed",
    )

    assert health.status is ProviderStatus.UNAVAILABLE
    assert health.error == "connection failed"
