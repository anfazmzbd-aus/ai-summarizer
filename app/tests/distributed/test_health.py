from app.distributed.workers import HealthStatus


def test_health_status_values():

    assert HealthStatus.HEALTHY.value == "healthy"

    assert HealthStatus.UNAVAILABLE.value == "unavailable"
