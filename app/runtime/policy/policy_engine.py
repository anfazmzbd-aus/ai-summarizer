from app.runtime.policy.execution_policy import (
    ExecutionPolicy,
)


class RuntimePolicyEngine:

    def __init__(
        self,
        policy: ExecutionPolicy | None = None,
    ):

        self._policy = policy or ExecutionPolicy()

    def resolve(
        self,
        context,
    ) -> ExecutionPolicy:
        """
        Resolve execution policy.

        Future:
        - tenant policies
        - agent-specific policies
        - dynamic rules
        """

        return self._policy
