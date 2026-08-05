from app.ai import AIRequest


def test_request():

    request = AIRequest(
        prompt="Summarize",
        model="demo",
    )

    assert request.temperature == 0.2
    assert request.max_tokens == 1024
