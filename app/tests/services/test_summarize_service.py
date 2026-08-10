from unittest.mock import Mock

from app.prompts.value_objects import PromptId, PromptVersion
from app.services.summarize_service import SummarizeService


def test_summarize_service_accepts_v9_runtime_dependencies():
    llm_service = Mock()
    prompt_manager = Mock()

    service = SummarizeService(
        llm_service=llm_service,
        prompt_manager=prompt_manager,
        prompt_id=PromptId("summary"),
        prompt_version=PromptVersion(1, 0, 0),
        model="mock-model",
    )

    assert service._llm_service is llm_service
    assert service._prompt_manager is prompt_manager
    assert service._prompt_id == PromptId("summary")
    assert service._prompt_version == PromptVersion(1, 0, 0)
    assert service._model == "mock-model"


def test_summarize_service_preserves_legacy_construction():
    service = SummarizeService()

    assert service._llm_service is None
    assert service._prompt_manager is None
    assert service._prompt_id is None
    assert service._prompt_version is None
    assert service._model is None
