from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPolicy:
    """
    Runtime execution policy.

    Controls execution behavior.
    """

    retry_enabled: bool = True
    max_retry_attempts: int = 3

    timeout_enabled: bool = True
    timeout_seconds: int = 30

    circuit_breaker_enabled: bool = True

    parallel_execution: bool = True
    max_workers: int = 4
