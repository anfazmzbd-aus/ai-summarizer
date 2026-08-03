"""
Resource-aware runtime policy.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope

from .decision import PolicyDecision
from .policy import Policy
from .resource_config import ResourceConfig
from .resource_state import ResourceState
from .result import PolicyResult


class ResourcePolicy(Policy):

    def __init__(
        self,
        config: ResourceConfig,
        state: ResourceState,
    ) -> None:

        self._config = config
        self._state = state

    def evaluate(
        self,
        task: TaskEnvelope,
    ) -> PolicyResult:

        if self._state.cpu_percent >= self._config.max_cpu_percent:
            return PolicyResult(
                PolicyDecision.DENY,
                "CPU utilization exceeded",
            )

        if self._state.memory_percent >= self._config.max_memory_percent:
            return PolicyResult(
                PolicyDecision.DENY,
                "Memory utilization exceeded",
            )

        if self._state.queue_pressure >= self._config.max_queue_pressure:
            return PolicyResult(
                PolicyDecision.DENY,
                "Queue pressure exceeded",
            )

        if self._state.worker_utilization >= self._config.max_worker_utilization:
            return PolicyResult(
                PolicyDecision.DENY,
                "Worker utilization exceeded",
            )

        return PolicyResult(PolicyDecision.ALLOW)
