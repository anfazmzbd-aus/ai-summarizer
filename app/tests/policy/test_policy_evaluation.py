from app.policy import (
    PolicyDecision,
    PolicyEvaluation,
)


def test_creation():

    evaluation = PolicyEvaluation(
        policy="QuotaPolicy",
        decision=PolicyDecision.ALLOW,
    )

    assert evaluation.policy == "QuotaPolicy"
    assert evaluation.decision is PolicyDecision.ALLOW
