from app.ai import SummarizationRequest


def test_request():

    request = SummarizationRequest(
        text="Hello",
        provider="fake",
        model="demo",
    )

    assert request.prompt_name == "summary"
