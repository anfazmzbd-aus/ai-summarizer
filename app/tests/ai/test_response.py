from app.ai import AIResponse


def test_response():

    response = AIResponse(
        text="Done",
        model="demo",
        prompt_tokens=10,
        completion_tokens=20,
    )

    assert response.total_tokens == 30
