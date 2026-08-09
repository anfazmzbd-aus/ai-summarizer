from unittest.mock import Mock

from app.orchestration.agents.summary import SummaryAgent
from app.orchestration.registry.agent_registry import AgentRegistry


def test_registry_creates_default_summary_agent():
    registry = AgentRegistry()

    agent = registry.get("summary").agent

    assert isinstance(agent, SummaryAgent)


def test_registry_accepts_injected_summary_agent():
    summary_agent = Mock(spec=SummaryAgent)

    registry = AgentRegistry(
        summary_agent=summary_agent,
    )

    assert registry.get("summary").agent is summary_agent


def test_registry_preserves_existing_agents():
    registry = AgentRegistry()

    assert registry.exists("summary")
    assert registry.exists("insights")
    assert registry.exists("actions")
