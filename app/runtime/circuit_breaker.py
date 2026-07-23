from datetime import datetime, timedelta

from .circuit_breaker_state import CircuitBreakerState


class CircuitBreaker:

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_seconds: int = 30,
    ):

        self.failure_threshold = failure_threshold

        self.recovery_timeout = timedelta(
            seconds=recovery_timeout_seconds,
        )

        self.failures = 0

        self.state = CircuitBreakerState.CLOSED

        self.opened_at = None

    def allow_request(self) -> bool:

        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:

            if datetime.utcnow() - self.opened_at >= self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                return True

            return False

        # HALF_OPEN
        return True

    def record_success(self):

        self.failures = 0

        self.state = CircuitBreakerState.CLOSED

        self.opened_at = None

    def record_failure(self):

        self.failures += 1

        if self.failures >= self.failure_threshold:

            self.state = CircuitBreakerState.OPEN

            self.opened_at = datetime.utcnow()
