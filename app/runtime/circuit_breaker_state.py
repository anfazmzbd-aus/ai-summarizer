from enum import Enum


class CircuitBreakerState(Enum):

    CLOSED = "closed"

    OPEN = "open"

    HALF_OPEN = "half_open"
