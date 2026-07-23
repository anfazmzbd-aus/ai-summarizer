from app.runtime.policy.policy_engine import (
    RuntimePolicyEngine,
)

from app.runtime.policy.execution_policy import (
    ExecutionPolicy,
)


def test_default_policy():

    engine = RuntimePolicyEngine()

    policy = engine.resolve(None)

    assert policy.retry_enabled is True
    assert policy.max_retry_attempts == 3


def test_custom_policy():

    policy = ExecutionPolicy(
        retry_enabled=False,
        max_retry_attempts=1,
    )

    engine = RuntimePolicyEngine(policy)

    result = engine.resolve(None)

    assert result.retry_enabled is False
    assert result.max_retry_attempts == 1


def test_policy_engine_resolves_context():

    engine = RuntimePolicyEngine()

    context = {"node": "summary"}

    policy = engine.resolve(context)

    assert policy is not None
