from unittest.mock import Mock

from app.services.summarize_service import SummarizeService


def test_summarize_service_builds_state_without_llm_service():
    service = SummarizeService()

    # state_builder = Mock()

    assert service._llm_service is None


def test_summarize_service_accepts_llm_service():
    llm_service = Mock()

    service = SummarizeService(
        llm_service=llm_service,
    )

    assert service._llm_service is llm_service
