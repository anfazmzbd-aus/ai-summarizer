from __future__ import annotations

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

import app.routes.file_extraction as file_route
from app.core.file_extraction import (
    EmptyExtractedTextError,
    EncryptedPdfError,
    FileExtractionResult,
    FileTooLargeError,
    FileType,
    InvalidPdfError,
    InvalidTextEncodingError,
    UnsupportedFileTypeError,
)
from app.main import app


client = TestClient(app)


def make_blank_pdf(
    *,
    encrypted: bool = False,
) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(
        width=612,
        height=792,
    )

    if encrypted:
        writer.encrypt("secret")

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def test_extract_txt_returns_public_response():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "notes.txt",
                b"Hello from file ingestion.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "text": "Hello from file ingestion.",
        "file": {
            "name": "notes.txt",
            "type": "txt",
            "size_bytes": len(b"Hello from file ingestion."),
            "page_count": None,
        },
    }


def test_extract_txt_normalizes_text():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "notes.txt",
                b"\r\n  Line one\r\nLine two  \r\n",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["text"] == ("Line one\nLine two")


def test_extract_txt_accepts_utf8_bom():
    content = b"\xef\xbb\xbfDocument content"

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "bom.txt",
                content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["text"] == "Document content"


def test_extract_txt_accepts_uppercase_extension():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "NOTES.TXT",
                b"Uppercase extension.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["file"]["type"] == "txt"


def test_extract_rejects_missing_file():
    response = client.post(
        "/api/v1/files/extract",
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("file_name", "content_type"),
    [
        (
            "document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
        ("document.csv", "text/csv"),
        ("document.exe", "application/octet-stream"),
        ("document", "application/octet-stream"),
    ],
)
def test_extract_rejects_unsupported_file_type(
    file_name,
    content_type,
):
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
    assert response.json() == {"detail": "Only TXT and PDF files are supported."}


def test_extract_rejects_empty_file_name():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "",
                b"content",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code in {
        415,
        422,
    }


def test_extract_rejects_invalid_utf8():
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
    assert response.json() == {"detail": "Text files must use UTF-8 encoding."}


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b" ",
        b"\r\n\t ",
    ],
)
def test_extract_rejects_txt_without_usable_text(content):
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "empty.txt",
                content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": ("The text file does not contain usable text.")
    }


def test_extract_rejects_invalid_pdf():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "invalid.pdf",
                b"Not actually a PDF.",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "The PDF file could not be read."}


def test_extract_rejects_pdf_without_extractable_text():
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
    assert response.json() == {
        "detail": ("The PDF file does not contain extractable text.")
    }


def test_extract_rejects_encrypted_pdf():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "encrypted.pdf",
                make_blank_pdf(
                    encrypted=True,
                ),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": ("Encrypted PDF files are not supported.")}


def test_extract_pdf_returns_public_metadata(
    monkeypatch,
):
    def fake_extract_pdf(
        *,
        file_name,
        content,
    ):
        return FileExtractionResult(
            text="Extracted PDF content.",
            file_name=file_name,
            file_type=FileType.PDF,
            size_bytes=len(content),
            page_count=3,
        )

    monkeypatch.setattr(
        file_route._file_extraction_service,
        "extract_pdf",
        fake_extract_pdf,
    )

    content = b"%PDF-test"

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "report.pdf",
                content,
                "application/pdf",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "text": "Extracted PDF content.",
        "file": {
            "name": "report.pdf",
            "type": "pdf",
            "size_bytes": len(content),
            "page_count": 3,
        },
    }


def test_extract_response_does_not_expose_private_metadata(
    monkeypatch,
):
    def fake_extract_pdf(
        *,
        file_name,
        content,
    ):
        return FileExtractionResult(
            text="Safe text.",
            file_name=file_name,
            file_type=FileType.PDF,
            size_bytes=len(content),
            page_count=1,
        )

    monkeypatch.setattr(
        file_route._file_extraction_service,
        "extract_pdf",
        fake_extract_pdf,
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "safe.pdf",
                b"%PDF-test",
                "application/pdf",
            )
        },
    )

    payload = response.json()
    metadata = payload["file"]

    assert set(metadata) == {
        "name",
        "type",
        "size_bytes",
        "page_count",
    }

    serialized = response.text.lower()

    assert "path" not in serialized
    assert "provider" not in serialized
    assert "api_key" not in serialized
    assert "base_url" not in serialized
    assert "organization" not in serialized


def test_extract_file_too_large_maps_to_413(
    monkeypatch,
):
    async def fail_read(
        file,
        *,
        max_bytes,
    ):
        raise FileTooLargeError("The uploaded file exceeds the maximum allowed size.")

    monkeypatch.setattr(
        file_route,
        "_read_upload_with_limit",
        fail_read,
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "large.txt",
                b"text",
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": ("The uploaded file exceeds the maximum allowed size.")
    }


@pytest.mark.parametrize(
    ("error", "expected_detail"),
    [
        (
            InvalidTextEncodingError("Text files must use UTF-8 encoding."),
            "Text files must use UTF-8 encoding.",
        ),
        (
            InvalidPdfError("The PDF file could not be read."),
            "The PDF file could not be read.",
        ),
        (
            EncryptedPdfError("Encrypted PDF files are not supported."),
            "Encrypted PDF files are not supported.",
        ),
        (
            EmptyExtractedTextError("The PDF file does not contain extractable text."),
            "The PDF file does not contain extractable text.",
        ),
    ],
)
def test_extraction_domain_errors_map_to_safe_422(
    monkeypatch,
    error,
    expected_detail,
):
    def fail_extract_pdf(
        *,
        file_name,
        content,
    ):
        raise error

    monkeypatch.setattr(
        file_route._file_extraction_service,
        "extract_pdf",
        fail_extract_pdf,
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "document.pdf",
                b"%PDF-test",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert response.json() == {"detail": expected_detail}


def test_extraction_error_does_not_expose_cause(
    monkeypatch,
):
    def fail_extract_pdf(
        *,
        file_name,
        content,
    ):
        try:
            raise RuntimeError("private parser implementation detail")
        except RuntimeError as cause:
            raise InvalidPdfError("The PDF file could not be read.") from cause

    monkeypatch.setattr(
        file_route._file_extraction_service,
        "extract_pdf",
        fail_extract_pdf,
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "document.pdf",
                b"%PDF-test",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 422
    assert "private parser implementation detail" not in response.text


def test_extract_does_not_require_ai_provider_configuration(
    monkeypatch,
):
    monkeypatch.delenv(
        "OPENAI_API_KEY",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_BASE_URL",
        raising=False,
    )
    monkeypatch.delenv(
        "OPENAI_MODEL",
        raising=False,
    )

    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "offline.txt",
                b"Offline extraction.",
                "text/plain",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["text"] == "Offline extraction."


def test_extraction_route_is_registered():
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/files/extract" in paths


def test_extraction_route_does_not_replace_summarize_route():
    paths = {route.path for route in app.routes if hasattr(route, "path")}

    assert "/api/v1/files/extract" in paths
    assert "/api/v1/summarize" in paths


@pytest.mark.parametrize(
    ("file_name", "content_type"),
    [
        ("notes.txt", "application/pdf"),
        ("report.pdf", "text/plain"),
        ("notes.txt", "application/octet-stream"),
        ("report.pdf", "application/octet-stream"),
    ],
)
def test_extract_rejects_extension_content_type_mismatch(
    file_name,
    content_type,
):
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
    assert response.json() == {
        "detail": "The uploaded file content type is not supported."
    }


def test_extract_rejects_missing_content_type():
    with pytest.raises(
        UnsupportedFileTypeError,
        match="The uploaded file content type is not supported.",
    ):
        file_route._validate_content_type(
            suffix=".txt",
            content_type=None,
        )


def test_extract_rejects_blank_content_type():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "notes.txt",
                b"content",
                "",
            )
        },
    )

    assert response.status_code == 415
    assert response.json() == {
        "detail": "The uploaded file content type is not supported."
    }


def test_extract_accepts_txt_content_type_parameters():
    response = client.post(
        "/api/v1/files/extract",
        files={
            "file": (
                "notes.txt",
                b"UTF-8 text",
                "text/plain; charset=utf-8",
            )
        },
    )

    assert response.status_code == 200
    assert response.json()["text"] == "UTF-8 text"


def test_extract_rejects_multiple_file_fields():
    response = client.post(
        "/api/v1/files/extract",
        files=[
            (
                "file",
                (
                    "one.txt",
                    b"First file",
                    "text/plain",
                ),
            ),
            (
                "file",
                (
                    "two.txt",
                    b"Second file",
                    "text/plain",
                ),
            ),
        ],
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Upload exactly one file."}
