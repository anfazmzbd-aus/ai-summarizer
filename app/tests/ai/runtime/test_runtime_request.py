from app.ai import AIRuntimeRequest


def test_runtime_request():

    request = AIRuntimeRequest(
        provider="fake",
        prompt_name="summary",
        model="demo",
    )

    assert request.provider == "fake"
