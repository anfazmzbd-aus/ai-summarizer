from unittest.mock import Mock

from app.providers.models import (
    LLMMessage,
    LLMRequest,
    MessageRole,
)

from app.providers.openai.adapter import (
    OpenAIAdapter,
)


def test_execute():

    transport = Mock()

    transport.client.responses.create.return_value = Mock(output_text="summary")

    adapter = OpenAIAdapter(transport)

    request = LLMRequest(
        model="gpt-5",
        messages=(
            LLMMessage(
                role=MessageRole.USER,
                content="hello",
            ),
        ),
    )

    result = adapter.execute(request)

    assert result.message.content == "summary"

    transport.client.responses.create.assert_called_once()
