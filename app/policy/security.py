"""
Runtime security policy.
"""

from __future__ import annotations

from app.distributed.protocols import TaskEnvelope

from .decision import PolicyDecision
from .policy import Policy
from .result import PolicyResult
from .security_config import SecurityConfig
from .security_context import SecurityContext


class SecurityPolicy(Policy):

    def __init__(
        self,
        config: SecurityConfig,
        context: SecurityContext,
    ) -> None:

        self._config = config
        self._context = context

    def evaluate(
        self,
        task: TaskEnvelope,
    ) -> PolicyResult:

        if self._config.require_authenticated and not self._context.authenticated:
            return PolicyResult(
                PolicyDecision.DENY,
                "Authentication required",
            )

        if self._config.require_tenant_id and not self._context.tenant_id:
            return PolicyResult(
                PolicyDecision.DENY,
                "Tenant ID required",
            )

        if (
            self._config.allowed_origins
            and self._context.origin not in self._config.allowed_origins
        ):
            return PolicyResult(
                PolicyDecision.DENY,
                "Origin not permitted",
            )

        if (
            self._config.allowed_agent_types
            and task.agent_type not in self._config.allowed_agent_types
        ):
            return PolicyResult(
                PolicyDecision.DENY,
                "Agent type not permitted",
            )

        return PolicyResult(PolicyDecision.ALLOW)
