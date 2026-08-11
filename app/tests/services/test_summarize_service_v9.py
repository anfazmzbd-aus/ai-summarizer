from app.services.summarize_service import SummarizeService


def test_summarize_service_uses_deterministic_v9_runtime():
    service = SummarizeService()

    result = service.run(
        "Revenue increased by 25 percent.",
    )

    assert result is not None


def test_summarize_service_does_not_use_legacy_summary_fallback():
    service = SummarizeService()

    result = service.run(
        "Revenue increased by 25 percent.",
    )

    assert result is not None

    assert result.result["summary"] == "Mock response generated successfully."


def test_summarize_service_uses_mock_provider_by_default():
    service = SummarizeService()

    result = service.run(
        "Production deployment completed successfully.",
    )

    assert result.result["summary"] == "Mock response generated successfully."
