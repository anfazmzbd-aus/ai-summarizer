from app.orchestration.contracts.execution_response import (
    ExecutionResponse,
)
from app.services.summarize_service import (
    SummarizeService,
)


def test_summarize_service_uses_deterministic_v9_runtime():
    service = SummarizeService()

    result = service.run(
        "Revenue increased by 25 percent.",
    )

    assert result is not None
    assert isinstance(
        result,
        ExecutionResponse,
    )

    assert result.status == "success"
    assert result.result["summary"] == ("Mock response generated successfully.")


def test_summarize_service_does_not_use_legacy_summary_fallback():
    service = SummarizeService()

    result = service.run(
        "Revenue increased by 25 percent.",
    )

    assert isinstance(
        result,
        ExecutionResponse,
    )

    assert result.result["summary"] == ("Mock response generated successfully.")

    assert result.result["summary"] != ("Revenue increased by 25 percent.")


def test_summarize_service_uses_mock_provider_by_default():
    service = SummarizeService()

    result = service.run(
        "Production deployment completed successfully.",
    )

    assert isinstance(
        result,
        ExecutionResponse,
    )

    assert result.status == "success"

    assert result.result["summary"] == ("Mock response generated successfully.")

    assert result.node_outputs["summary"] == {
        "summary": "Mock response generated successfully."
    }
