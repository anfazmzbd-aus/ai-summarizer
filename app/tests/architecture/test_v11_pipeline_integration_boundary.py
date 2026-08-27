"""V11 M2.1 V9 pipeline integration-boundary tests."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

ADAPTER = ROOT / "app" / "core" / "summarization_pipeline_adapter.py"
FACTORY = ROOT / "app" / "core" / "summarization_pipeline_factory.py"
PIPELINE = ROOT / "app" / "summarization" / "pipeline.py"
APPLICATION = ROOT / "app" / "api" / "application.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_adapter_uses_existing_v9_pipeline() -> None:
    content = read(ADAPTER)

    assert "app.summarization.pipeline" in content
    assert "SummarizationPipeline" in content


def test_adapter_does_not_import_provider_implementations() -> None:
    content = read(ADAPTER)

    assert "app.providers" not in content
    assert "app.ai.providers" not in content


def test_adapter_does_not_import_v10_intelligence() -> None:
    content = read(ADAPTER)

    assert "app.intelligence" not in content


def test_adapter_does_not_duplicate_strategy_implementations() -> None:
    content = read(ADAPTER)

    assert "DirectSummarizationStrategy" not in content
    assert "MapReduceSummarizationStrategy" not in content
    assert "HierarchicalSummarizationStrategy" not in content


def test_factory_uses_existing_text_chunker_and_pipeline() -> None:
    content = read(FACTORY)

    assert "TextChunker" in content
    assert "SummarizationPipeline" in content


def test_existing_v9_pipeline_remains_provider_independent() -> None:
    content = read(PIPELINE)

    assert "app.providers" not in content
    assert "app.ai.providers" not in content


def test_canonical_application_uses_pipeline_adapter() -> None:
    content = read(APPLICATION)

    assert "AsyncSummarizationPipelineAdapter" in content
    assert "build_summarization_pipeline_adapter" in content


def test_application_does_not_reimplement_v9_strategies() -> None:
    content = read(APPLICATION)

    assert "DirectSummarizationStrategy" not in content
    assert "MapReduceSummarizationStrategy" not in content
    assert "HierarchicalSummarizationStrategy" not in content


def test_application_does_not_import_v10_intelligence_yet() -> None:
    content = read(APPLICATION)

    assert "app.intelligence" not in content


def test_application_owns_cross_call_usage_accounting() -> None:
    content = read(APPLICATION)

    assert "prompt_tokens +=" in content
    assert "completion_tokens +=" in content


def test_v9_pipeline_does_not_gain_provider_usage_accounting() -> None:
    content = read(PIPELINE)

    assert "prompt_tokens" not in content
    assert "completion_tokens" not in content


API_INTEGRATION_TEST = (
    ROOT / "app" / "tests" / "integration" / "test_v11_api_pipeline.py"
)


def test_api_integration_exercises_canonical_application_boundary() -> None:
    content = read(API_INTEGRATION_TEST)

    assert "/api/v1/summarize" in content
    assert "SummarizationApplication" in content
    assert "AsyncSummarizationPipelineAdapter" in content


def test_api_integration_does_not_use_live_provider() -> None:
    content = read(API_INTEGRATION_TEST)

    assert "OpenAI(" not in content
    assert "AzureOpenAI" not in content
    assert "Ollama" not in content


def test_m2_application_does_not_implement_resilience_policy() -> None:
    content = read(APPLICATION)

    assert "Retry" not in content
    assert "Fallback" not in content
    assert "app.summarization.resilience" not in content
    assert "app.summarization.quality_adaptive" not in content


def test_m2_adapter_does_not_swallow_runtime_errors() -> None:
    content = read(ADAPTER)

    assert "except RuntimeError" not in content
