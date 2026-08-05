from app.ai import (
    AIResponse,
    AIRuntimeResponse,
)


def test_runtime_response():

    response = AIRuntimeResponse(
        prompt="Prompt",
        response=AIResponse(
            text="Answer",
            model="demo",
        ),
    )

    assert response.response.text == "Answer"
