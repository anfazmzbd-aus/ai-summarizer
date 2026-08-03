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


def test_report():

    engine = PolicyEngine([AllowPolicy()])

    report = engine.evaluate_report(task())

    assert report.allowed


def test_short_circuit():

    engine = PolicyEngine(
        [
            DenyPolicy(),
            AllowPolicy(),
        ]
    )

    report = engine.evaluate_report(task())

    assert len(report.evaluations) == 1


def test_exception():

    engine = PolicyEngine([DenyPolicy()])

    with pytest.raises(PolicyViolation):

        engine.evaluate(task())
