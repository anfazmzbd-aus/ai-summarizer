from app.plugins import AgentCapability


def test_capability():

    capability = AgentCapability(
        "custom-summary",
        "1.0",
    )

    assert capability.name == "custom-summary"
