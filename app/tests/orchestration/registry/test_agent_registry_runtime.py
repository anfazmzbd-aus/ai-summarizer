from unittest.mock import Mock

from app.orchestration.registry.agent_registry import AgentRegistry
from app.prompts.value_objects import (
    PromptId,
    PromptVersion,
)

from app.orchestration.agents.summary import SummaryAgent


def test_registry_preserves_v8_default_behavior():
    registry = AgentRegistry()

    assert registry.exists("summary")
    assert registry.exists("insights")
    assert registry.exists("actions")


def test_registry_accepts_v9_runtime_dependencies():
    prompt_manager = Mock()
    llm_service = Mock()

    registry = AgentRegistry(
        prompt_manager=prompt_manager,
        llm_service=llm_service,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    agent = registry.get("summary").agent

    assert isinstance(agent, SummaryAgent)
    assert agent._prompt_manager is prompt_manager
    assert agent._llm_service is llm_service
    assert agent._prompt_id == PromptId("summary")
    assert agent._prompt_version == PromptVersion(1, 0, 0)
    assert agent._model == "mock-model"


def test_registry_injects_prompt_manager():
    prompt_manager = Mock()
    llm_service = Mock()

    registry = AgentRegistry(
        prompt_manager=prompt_manager,
        llm_service=llm_service,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    agent = registry.get("summary").agent

    assert agent._prompt_manager is prompt_manager


def test_registry_injects_llm_service():
    prompt_manager = Mock()
    llm_service = Mock()

    registry = AgentRegistry(
        prompt_manager=prompt_manager,
        llm_service=llm_service,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    agent = registry.get("summary").agent

    assert agent._llm_service is llm_service


def test_registry_preserves_agent_graph_dependencies():
    registry = AgentRegistry()

    assert registry.get("summary").dependencies == ()
    assert registry.get("insights").dependencies == ("summary",)
    assert registry.get("actions").dependencies == ("summary",)
