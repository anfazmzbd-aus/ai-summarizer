"""
Quota policy.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope

from .decision import PolicyDecision
from .policy import Policy
from .quota_config import QuotaConfig
from .quota_state import QuotaState
from .result import PolicyResult


class QuotaPolicy(Policy):

    def __init__(
        self,
        config: QuotaConfig,
        state: QuotaState,
    ) -> None:

        self._config = config
        self._state = state

    def evaluate(
        self,
        task: TaskEnvelope,
    ) -> PolicyResult:

        if self._state.queue_depth >= self._config.max_queue_depth:
            return PolicyResult(
                PolicyDecision.DENY,
                "Queue depth exceeded",
            )

        if self._state.concurrent_tasks >= self._config.max_concurrent_tasks:
            return PolicyResult(
                PolicyDecision.DENY,
                "Concurrent task limit exceeded",
            )

        if self._state.worker_tasks >= self._config.max_worker_tasks:
            return PolicyResult(
                PolicyDecision.DENY,
                "Worker task limit exceeded",
            )

        return PolicyResult(PolicyDecision.ALLOW)
