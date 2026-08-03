from app.distributed.protocols import TaskEnvelope

from app.policy import (
    PolicyDecision,
    QuotaConfig,
    QuotaPolicy,
    QuotaState,
)


def task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


def test_allow():

    policy = QuotaPolicy(
        QuotaConfig(),
        QuotaState(),
    )

    result = policy.evaluate(task())

    assert result.decision is PolicyDecision.ALLOW


def test_queue_limit():

    state = QuotaState(
        queue_depth=1000,
    )

    policy = QuotaPolicy(
        QuotaConfig(),
        state,
    )

    result = policy.evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_concurrent_limit():

    state = QuotaState(
        concurrent_tasks=100,
    )

    policy = QuotaPolicy(
        QuotaConfig(),
        state,
    )

    result = policy.evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_worker_limit():

    state = QuotaState(
        worker_tasks=10,
    )

    policy = QuotaPolicy(
        QuotaConfig(),
        state,
    )

    result = policy.evaluate(task())

    assert result.decision is PolicyDecision.DENY
