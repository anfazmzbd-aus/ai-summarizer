from app.policy import (
    PolicyDecision,
    PolicyResult,
)


def test_allowed():

    result = PolicyResult(PolicyDecision.ALLOW)

    assert result.allowed


def test_denied():

    result = PolicyResult(PolicyDecision.DENY)

    assert not result.allowed
