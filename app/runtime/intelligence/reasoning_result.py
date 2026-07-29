from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReasoningResult:
    workload_size: int
    estimated_parallelism: int
    cache_available: bool
    cancellation_requested: bool
    timeout_risk: bool
    retry_pressure: bool
    policy_restricted: bool
