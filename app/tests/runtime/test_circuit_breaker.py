from app.runtime.circuit_breaker import CircuitBreaker
from app.runtime.circuit_breaker_state import (
    CircuitBreakerState,
)


def test_initial_state_is_closed():

    breaker = CircuitBreaker()

    assert breaker.state == CircuitBreakerState.CLOSED


def test_closed_state_allows_requests():

    breaker = CircuitBreaker()

    assert breaker.allow_request() is True


def test_failure_threshold_opens_circuit():

    breaker = CircuitBreaker(
        failure_threshold=2,
    )

    breaker.record_failure()
    breaker.record_failure()

    assert breaker.state == CircuitBreakerState.OPEN


def test_open_state_blocks_requests():

    breaker = CircuitBreaker(
        failure_threshold=1,
    )

    breaker.record_failure()

    assert breaker.allow_request() is False


def test_success_resets_circuit():

    breaker = CircuitBreaker(
        failure_threshold=1,
    )

    breaker.record_failure()

    assert breaker.state == CircuitBreakerState.OPEN

    breaker.record_success()

    assert breaker.state == CircuitBreakerState.CLOSED
    assert breaker.failures == 0


def test_open_state_moves_to_half_open_after_timeout():

    breaker = CircuitBreaker(
        failure_threshold=1,
        recovery_timeout_seconds=0,
    )

    breaker.record_failure()

    assert breaker.state == CircuitBreakerState.OPEN

    assert breaker.allow_request() is True

    assert breaker.state == CircuitBreakerState.HALF_OPEN
