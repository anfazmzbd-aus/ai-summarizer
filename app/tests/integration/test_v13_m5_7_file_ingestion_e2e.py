"""V13 M5.7 end-to-end file-ingestion certification."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.core.file_extraction import (
    FileExtractionResult,
    FileType,
)
from app.core.product_model_catalogue import (
    ProductModel,
    ProductModelCatalogue,
)
from app.main import app
from app.routes import ai as ai_route
from app.routes import file_extraction as file_route


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = ROOT / "static" / "app.js"

client = TestClient(app)


def read_script() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def build_catalogue() -> ProductModelCatalogue:
    return ProductModelCatalogue(
        (
            ProductModel(
                id="balanced",
                label="Balanced",
                provider="fake",
                model="runtime-balanced",
                is_default=True,
            ),
            ProductModel(
                id="quality",
                label="Quality",
                provider="fake",
                model="runtime-quality",
                is_default=False,
            ),
        )
    )


class FakeMetadata:
    strategy = "direct"
    chunk_count = 1
    intelligence_mode = "preserve"
    trace_id = "m5-7-trace"
    explainability_summary = "preserved"
    attributes = {}


class FakeResult:
    def __init__(
        self,
        *,
        model: str,
        summary: str = "certified file summary",
    ) -> None:
        self.summary = summary
        self.model = model
        self.prompt_tokens = 20
        self.completion_tokens = 30
        self.metadata = FakeMetadata()

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


def make_blank_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(
        width=612,
        height=792,
    )

    output = BytesIO()
    writer.write(output)

    return output.getvalue()


def test_txt_extraction_returns_normalized_source_text() -> None:
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "certification.txt",
                b"\r\n  File ingestion source.\r\n" b"Second line.  \r\n",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["text"] == ("File ingestion source.\nSecond line.")

    assert payload["file"] == {
        "name": "certification.txt",
        "type": "txt",
        "size_bytes": len(b"\r\n  File ingestion source.\r\n" b"Second line.  \r\n"),
        "page_count": None,
    }


def test_txt_extracted_text_enters_canonical_application(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
            captured["request"] = request

            return FakeResult(
                model=request.model or "",
            )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    extraction_response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.txt",
                b"\r\n  Exact TXT source.\r\n" b"Operational details.  \r\n",
                "text/plain",
            )
        },
    )

    assert extraction_response.status_code == 200

    extracted_text = extraction_response.json()["text"]

    summary_response = client.post(
        "/api/v1/summarize",
        json={
            "text": extracted_text,
            "product_model": "quality",
            "summary_type": "executive",
            "summary_length": "detailed",
            "instructions": "Focus on operational risks.",
        },
    )

    assert summary_response.status_code == 200

    request = captured["request"]

    assert request.text == extracted_text
    assert request.text == ("Exact TXT source.\nOperational details.")

    assert request.provider == "fake"
    assert request.model == "runtime-quality"

    assert request.summary_type.value == "executive"
    assert request.summary_length.value == "detailed"

    assert request.instructions == ("Focus on operational risks.")


def test_txt_file_flow_returns_product_safe_summary(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()

    class FakeApplication:
        async def summarize(self, request):
            return FakeResult(
                model=request.model or "",
                summary="TXT certification summary.",
            )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    extraction_response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.txt",
                b"TXT certification source.",
                "text/plain",
            )
        },
    )

    extracted_text = extraction_response.json()["text"]

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": extracted_text,
            "product_model": "balanced",
        },
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["summary"] == ("TXT certification summary.")

    assert payload["model"] == "runtime-balanced"
    assert payload["prompt_tokens"] == 20
    assert payload["completion_tokens"] == 30
    assert payload["total_tokens"] == 50


def test_pdf_extracted_text_enters_canonical_application(
    monkeypatch,
) -> None:
    catalogue = build_catalogue()
    captured = {}

    def fake_extract_pdf(
        *,
        file_name,
        content,
    ):
        return FileExtractionResult(
            text=("Extracted PDF certification source.\n" "Second PDF line."),
            file_name=file_name,
            file_type=FileType.PDF,
            size_bytes=len(content),
            page_count=2,
        )

    class FakeApplication:
        async def summarize(self, request):
            captured["request"] = request

            return FakeResult(
                model=request.model or "",
            )

    monkeypatch.setattr(
        file_route._file_extraction_service,
        "extract_pdf",
        fake_extract_pdf,
    )

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        lambda: catalogue,
    )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    pdf_content = make_blank_pdf()

    extraction_response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "report.pdf",
                pdf_content,
                "application/pdf",
            )
        },
    )

    assert extraction_response.status_code == 200

    extraction_payload = extraction_response.json()

    assert extraction_payload["file"]["type"] == "pdf"
    assert extraction_payload["file"]["page_count"] == 2

    summary_response = client.post(
        "/api/v1/summarize",
        json={
            "text": extraction_payload["text"],
            "product_model": "quality",
            "summary_type": "technical",
            "summary_length": "short",
            "instructions": "Preserve technical terms.",
        },
    )

    assert summary_response.status_code == 200

    request = captured["request"]

    assert request.text == ("Extracted PDF certification source.\n" "Second PDF line.")

    assert request.provider == "fake"
    assert request.model == "runtime-quality"
    assert request.summary_type.value == "technical"
    assert request.summary_length.value == "short"

    assert request.instructions == ("Preserve technical terms.")


def test_extraction_does_not_invoke_summarization_application(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True

            raise AssertionError("extraction must not invoke summarization")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.txt",
                b"Extraction only.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert application_called is False


def test_extraction_does_not_build_product_model_catalogue(
    monkeypatch,
) -> None:
    catalogue_called = False

    def fail_catalogue_build():
        nonlocal catalogue_called
        catalogue_called = True

        raise AssertionError("extraction must not resolve product models")

    monkeypatch.setattr(
        ai_route,
        "build_product_model_catalogue",
        fail_catalogue_build,
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.txt",
                b"Extraction only.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert catalogue_called is False


def test_extraction_failure_cannot_reach_application(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True

            raise AssertionError("invalid extraction must not summarize")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.docx",
                b"unsupported",
                (
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
            )
        },
    )

    assert response.status_code == 415
    assert application_called is False


@pytest.mark.parametrize(
    (
        "file_name",
        "content_type",
    ),
    [
        (
            "source.txt",
            "application/pdf",
        ),
        (
            "source.pdf",
            "text/plain",
        ),
        (
            "source.txt",
            "application/octet-stream",
        ),
        (
            "source.pdf",
            "application/octet-stream",
        ),
    ],
)
def test_mime_mismatch_is_rejected_before_summarization(
    monkeypatch,
    file_name,
    content_type,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True

            raise AssertionError("invalid MIME must not summarize")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                file_name,
                b"content",
                content_type,
            )
        },
    )

    assert response.status_code == 415
    assert application_called is False


def test_multiple_files_are_rejected_before_summarization(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True

            raise AssertionError("multiple files must not summarize")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/files/extract",
        files=[
            (
                "file",
                (
                    "first.txt",
                    b"First.",
                    "text/plain",
                ),
            ),
            (
                "file",
                (
                    "second.txt",
                    b"Second.",
                    "text/plain",
                ),
            ),
        ],
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Upload exactly one file."}

    assert application_called is False


def test_invalid_utf8_cannot_reach_summarization(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True

            raise AssertionError("invalid text must not summarize")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "invalid.txt",
                b"\xff\xfe\xfa",
                "text/plain",
            )
        },
    )

    assert response.status_code == 422
    assert application_called is False


def test_blank_pdf_cannot_reach_summarization(
    monkeypatch,
) -> None:
    application_called = False

    class FakeApplication:
        async def summarize(self, request):
            nonlocal application_called
            application_called = True

            raise AssertionError("blank PDF must not summarize")

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "blank.pdf",
                make_blank_pdf(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert application_called is False


def test_extraction_response_contains_no_provider_configuration() -> None:
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.txt",
                b"Safe source.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    serialized = response.text.lower()

    assert "provider" not in serialized
    assert "api_key" not in serialized
    assert "base_url" not in serialized
    assert "organization" not in serialized
    assert "prompt" not in serialized


def test_extraction_response_contains_only_public_file_metadata() -> None:
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "source.txt",
                b"Safe source.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    metadata = response.json()["file"]

    assert set(metadata) == {
        "name",
        "type",
        "size_bytes",
        "page_count",
    }


def test_frontend_extraction_and_summarization_endpoints_are_separate() -> None:
    script = read_script()

    assert '"/api/v1/files/extract"' in script
    assert 'fetch("/api/v1/summarize"' in script

    extraction_start = script.index("async function extractFile")

    extraction_end = script.index(
        "function handleSelectedFiles",
        extraction_start,
    )

    extraction_source = script[extraction_start:extraction_end]

    assert "/api/v1/summarize" not in extraction_source


def test_frontend_places_extracted_text_in_shared_source_workspace() -> None:
    script = read_script()

    extraction_start = script.index("async function extractFile")

    extraction_end = script.index(
        "function handleSelectedFiles",
        extraction_start,
    )

    extraction_source = script[extraction_start:extraction_end]

    assert "inputText.value = payload.text;" in extraction_source

    assert "updateInputState();" in extraction_source


def test_frontend_requires_explicit_submit_after_extraction() -> None:
    script = read_script()

    extraction_start = script.index("async function extractFile")

    extraction_end = script.index(
        "function handleSelectedFiles",
        extraction_start,
    )

    extraction_source = script[extraction_start:extraction_end]

    assert "summaryForm.submit" not in extraction_source
    assert "summaryForm.requestSubmit" not in extraction_source
    assert "/api/v1/summarize" not in extraction_source


def test_frontend_summary_request_uses_shared_source_text() -> None:
    script = read_script()

    submit_start = script.index("summaryForm.addEventListener(")

    submit_source = script[submit_start:]

    assert "const normalizedText = inputText.value.trim();" in submit_source

    assert "text: normalizedText" in submit_source


def test_frontend_file_flow_preserves_product_controls() -> None:
    script = read_script()

    submit_start = script.index("summaryForm.addEventListener(")

    submit_source = script[submit_start:]

    assert "product_model: modelSelection.value" in submit_source

    assert "summary_type: summaryType.value" in submit_source

    assert "summary_length: summaryLength.value" in submit_source

    assert "customInstructions.value.trim() || null" in submit_source


def test_frontend_contains_only_one_summarization_fetch() -> None:
    script = read_script()

    assert script.count('fetch("/api/v1/summarize"') == 1


def test_file_ingestion_introduces_no_alternate_summary_endpoint() -> None:
    script = read_script()

    forbidden_endpoints = (
        "/api/v1/files/summarize",
        "/api/v1/upload/summarize",
        "/api/v1/document/summarize",
        "/api/v1/product-summarize",
        "/api/v1/file-summarize",
    )

    for endpoint in forbidden_endpoints:
        assert endpoint not in script


@pytest.mark.parametrize(
    "private_name",
    [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "OPENAI_ORGANIZATION",
        "AI_PRODUCT_MODELS",
    ],
)
def test_file_ingestion_frontend_contains_no_private_configuration(
    private_name: str,
) -> None:
    script = read_script()

    assert private_name not in script


def test_file_extraction_endpoint_and_summarization_endpoint_coexist() -> None:
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/files/extract" in paths
    assert "/api/v1/summarize" in paths


def test_file_ingestion_preserves_legacy_text_summarization(
    monkeypatch,
) -> None:
    captured = {}

    class FakeApplication:
        async def summarize(self, request):
            captured["request"] = request

            return FakeResult(
                model=request.model or "",
                summary="legacy text summary",
            )

    monkeypatch.setattr(
        ai_route,
        "build_summarization_application",
        lambda: FakeApplication(),
    )

    response = client.post(
        "/api/v1/summarize",
        json={
            "text": "Legacy pasted source.",
            "provider": "fake",
            "model": "demo",
        },
    )

    assert response.status_code == 200

    request = captured["request"]

    assert request.text == "Legacy pasted source."
    assert request.provider == "fake"
    assert request.model == "demo"

    assert response.json()["summary"] == ("legacy text summary")
