from app.api.dependencies import (
    build_summarization_service,
)


def test_dependencies():

    service = build_summarization_service()

    assert service is not None
