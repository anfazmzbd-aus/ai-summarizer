from unittest.mock import Mock

from app.orchestration.agents.summary import SummaryAgent
from app.orchestration.state.state_builder import StateBuilder
from app.providers.models import (
    FinishReason,
    LLMMessage,
    LLMResponse,
    Usage,
    MessageRole,
)
from app.prompts.value_objects import (
    PromptId,
    PromptVersion,
)


def _response(
    content: str,
) -> LLMResponse:
    return LLMResponse(
        message=LLMMessage(
            role=MessageRole.ASSISTANT,
            content=content,
        ),
        model="mock-model",
        finish_reason=FinishReason.STOP,
        usage=Usage(),
        latency_ms=1.0,
    )


def test_legacy_summary_agent_preserves_v8_behavior():
    agent = SummaryAgent.legacy()

    state = StateBuilder.build(
        "A" * 200,
    )

    result = agent.run(state)

    assert result == {
        "summary": "A" * 150,
    }


def test_default_summary_agent_is_legacy_compatible():
    agent = SummaryAgent()

    state = StateBuilder.build(
        "Revenue increased by 25 percent.",
    )

    result = agent.run(state)

    assert result["summary"] == ("Revenue increased by 25 percent.")


def test_ai_summary_agent_renders_prompt_and_executes_llm():
    prompt_manager = Mock()
    llm_service = Mock()

    prompt_manager.render.return_value = Mock(
        system_prompt="Summarize the supplied text.",
        user_prompt="Revenue increased by 25 percent.",
    )

    llm_service.execute.return_value = _response("Revenue increased by 25 percent.")

    agent = SummaryAgent(
        prompt_manager=prompt_manager,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
        llm_service=llm_service,
    )

    state = StateBuilder.build(
        "Revenue increased by 25 percent.",
    )

    result = agent.run(state)

    assert result == {
        "summary": "Revenue increased by 25 percent.",
    }

    prompt_manager.render.assert_called_once_with(
        prompt_id=PromptId("summary"),
        version=PromptVersion(1, 0, 0),
        variables={
            "text": "Revenue increased by 25 percent.",
        },
    )

    llm_service.execute.assert_called_once()

    request = llm_service.execute.call_args.args[0]

    assert request.model == "mock-model"
    assert request.stream is False

    assert len(request.messages) == 2

    assert request.messages[0].role is MessageRole.SYSTEM
    assert request.messages[0].content == ("Summarize the supplied text.")

    assert request.messages[1].role is MessageRole.USER
    assert request.messages[1].content == ("Revenue increased by 25 percent.")


def test_ai_summary_agent_uses_response_message_content():
    prompt_manager = Mock()
    llm_service = Mock()

    prompt_manager.render.return_value = Mock(
        system_prompt="Summarize.",
        user_prompt="Input text.",
    )

    llm_service.execute.return_value = _response("Generated AI summary.")

    agent = SummaryAgent(
        prompt_manager=prompt_manager,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
        llm_service=llm_service,
    )

    state = StateBuilder.build("Input text.")

    result = agent.run(state)

    assert result["summary"] == "Generated AI summary."


def test_ai_summary_agent_strips_response_whitespace():
    prompt_manager = Mock()
    llm_service = Mock()

    prompt_manager.render.return_value = Mock(
        system_prompt="Summarize.",
        user_prompt="Input text.",
    )

    llm_service.execute.return_value = _response(
        "  Generated summary.  ",
    )

    agent = SummaryAgent(
        prompt_manager=prompt_manager,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
        llm_service=llm_service,
    )

    state = StateBuilder.build("Input text.")

    result = agent.run(state)

    assert result["summary"] == "Generated summary."


def test_ai_mode_requires_all_runtime_dependencies():
    agent = SummaryAgent(
        prompt_manager=Mock(),
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    assert agent.is_ai_enabled is False

    state = StateBuilder.build(
        "Revenue increased.",
    )

    result = agent.run(state)

    assert result["summary"] == "Revenue increased."


def test_ai_mode_is_detected_when_all_dependencies_are_present():
    agent = SummaryAgent(
        prompt_manager=Mock(),
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
        llm_service=Mock(),
    )

    assert agent.is_ai_enabled is True
