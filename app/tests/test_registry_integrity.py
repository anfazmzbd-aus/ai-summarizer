from app.orchestration.registry.agent_registry import (
    AgentRegistry,
)


def test_registry():

    registry = AgentRegistry()

    assert registry.exists("summary")
