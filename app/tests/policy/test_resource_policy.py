from app.distributed.protocols import TaskEnvelope

from app.policy import (
    PolicyDecision,
    ResourceConfig,
    ResourcePolicy,
    ResourceState,
)


def task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


def test_allow():

    policy = ResourcePolicy(
        ResourceConfig(),
        ResourceState(),
    )

    result = policy.evaluate(task())

    assert result.decision is PolicyDecision.ALLOW


def test_cpu_limit():

    state = ResourceState(cpu_percent=95.0)

    result = ResourcePolicy(
        ResourceConfig(),
        state,
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_memory_limit():

    state = ResourceState(memory_percent=95.0)

    result = ResourcePolicy(
        ResourceConfig(),
        state,
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_queue_pressure_limit():

    state = ResourceState(queue_pressure=0.95)

    result = ResourcePolicy(
        ResourceConfig(),
        state,
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_worker_utilization_limit():

    state = ResourceState(worker_utilization=1.0)

    result = ResourcePolicy(
        ResourceConfig(),
        state,
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY
