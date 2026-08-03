from app.policy import PolicyDecision


def test_decisions():

    assert PolicyDecision.ALLOW.value == "allow"
    assert PolicyDecision.DENY.value == "deny"
