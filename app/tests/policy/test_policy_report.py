from app.policy import (
    PolicyDecision,
    PolicyEvaluation,
    PolicyReport,
)


def test_allow_report():

    report = PolicyReport()

    report.evaluations.append(
        PolicyEvaluation(
            "A",
            PolicyDecision.ALLOW,
        )
    )

    assert report.allowed


def test_deny_report():

    report = PolicyReport()

    report.evaluations.append(
        PolicyEvaluation(
            "A",
            PolicyDecision.DENY,
        )
    )

    assert not report.allowed
