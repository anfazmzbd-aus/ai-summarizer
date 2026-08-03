import pytest

from app.distributed.protocols import TaskEnvelope

from app.policy import (
    Policy,
    PolicyDecision,
    PolicyEngine,
    PolicyResult,
    PolicyViolation,
)


class AllowPolicy(Policy):

    def evaluate(self, task):

        return PolicyResult(PolicyDecision.ALLOW)


class DenyPolicy(Policy):

    def evaluate(self, task):

        return PolicyResult(
            PolicyDecision.DENY,
            "blocked",
        )


def task():

    return TaskEnvelope(
        task_id="1",
        execution_id="exec",
        node_id="node",
        agent_type="summary",
    )


def test_allow():

    engine = PolicyEngine([AllowPolicy()])

    engine.evaluate(task())


def test_deny():

    engine = PolicyEngine([DenyPolicy()])

    with pytest.raises(PolicyViolation):

        engine.evaluate(task())
