from app.ai import SummarizationResponse


def test_response():

    response = SummarizationResponse(
        summary="Short",
        prompt="Prompt",
        model="demo",
        prompt_tokens=15,
        completion_tokens=25,
    )

    assert response.total_tokens == 40
