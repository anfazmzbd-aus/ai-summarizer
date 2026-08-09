from unittest.mock import Mock

from app.orchestration.agents.runtime import AgentRuntime
from app.prompts.value_objects import (
    PromptId,
    PromptVersion,
)


def test_agent_runtime_is_immutable():
    runtime = AgentRuntime(
        prompt_manager=Mock(),
        llm_service=Mock(),
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    assert runtime.model == "mock-model"


def test_agent_runtime_contains_required_dependencies():
    prompt_manager = Mock()
    llm_service = Mock()

    runtime = AgentRuntime(
        prompt_manager=prompt_manager,
        llm_service=llm_service,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    assert runtime.prompt_manager is prompt_manager
    assert runtime.llm_service is llm_service
