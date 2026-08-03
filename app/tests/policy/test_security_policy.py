from app.distributed.protocols import TaskEnvelope

from app.policy import (
    PolicyDecision,
    SecurityConfig,
    SecurityContext,
    SecurityPolicy,
)


def task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


def test_allow():

    result = SecurityPolicy(
        SecurityConfig(),
        SecurityContext(),
    ).evaluate(task())

    assert result.decision is PolicyDecision.ALLOW


def test_authentication_required():

    result = SecurityPolicy(
        SecurityConfig(
            require_authenticated=True,
        ),
        SecurityContext(
            authenticated=False,
        ),
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_tenant_required():

    result = SecurityPolicy(
        SecurityConfig(
            require_tenant_id=True,
        ),
        SecurityContext(),
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_origin_validation():

    result = SecurityPolicy(
        SecurityConfig(
            allowed_origins={"internal"},
        ),
        SecurityContext(
            origin="external",
        ),
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY


def test_agent_validation():

    result = SecurityPolicy(
        SecurityConfig(
            allowed_agent_types={"research"},
        ),
        SecurityContext(),
    ).evaluate(task())

    assert result.decision is PolicyDecision.DENY
