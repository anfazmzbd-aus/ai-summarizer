from app.ai import AIRuntimeRequest


def test_runtime_request():

    request = AIRuntimeRequest(
        provider="fake",
        prompt_name="summary",
        model="demo",
    )

    assert request.provider == "fake"


def test_runtime_request_defaults_to_prompt_version_1_0():
    request = AIRuntimeRequest(
        provider="fake",
        prompt_name="summary",
        model="demo",
    )

    assert request.prompt_version == "1.0"
