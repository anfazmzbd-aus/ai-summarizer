from __future__ import annotations

from io import BytesIO

import pytest
from pypdf import PdfWriter

import app.core.file_extraction as file_extraction
from app.core.file_extraction import (
    EmptyExtractedTextError,
    EncryptedPdfError,
    FileExtractionResult,
    FileExtractionService,
    FileTooLargeError,
    FileType,
    InvalidPdfError,
    UnsupportedFileTypeError,
)


def make_blank_pdf(
    *,
    pages: int = 1,
    encrypted: bool = False,
) -> bytes:
    writer = PdfWriter()

    for _ in range(pages):
        writer.add_blank_page(
            width=612,
            height=792,
        )

    if encrypted:
        writer.encrypt("secret")

    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class FakePage:
    def __init__(
        self,
        text: str | None,
    ) -> None:
        self._text = text

    def extract_text(self) -> str | None:
        return self._text


class FailingPage:
    def extract_text(self) -> str:
        raise RuntimeError("private parser failure")


class FakeReader:
    def __init__(
        self,
        pages,
        *,
        encrypted: bool = False,
    ) -> None:
        self.pages = pages
        self.is_encrypted = encrypted


def test_extract_pdf_returns_structured_result(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage("First page."),
                FakePage("Second page."),
            ]
        ),
    )

    content = b"%PDF-test"

    result = FileExtractionService().extract_pdf(
        file_name="report.pdf",
        content=content,
    )

    assert isinstance(result, FileExtractionResult)
    assert result.text == "First page.\n\nSecond page."
    assert result.file_name == "report.pdf"
    assert result.file_type is FileType.PDF
    assert result.size_bytes == len(content)
    assert result.page_count == 2


def test_extract_pdf_accepts_uppercase_extension(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader([FakePage("PDF text.")]),
    )

    result = FileExtractionService().extract_pdf(
        file_name="REPORT.PDF",
        content=b"%PDF-test",
    )

    assert result.file_name == "REPORT.PDF"
    assert result.file_type is FileType.PDF


def test_extract_pdf_trims_file_name_outer_whitespace(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader([FakePage("PDF text.")]),
    )

    result = FileExtractionService().extract_pdf(
        file_name="  report.pdf  ",
        content=b"%PDF-test",
    )

    assert result.file_name == "report.pdf"


def test_extract_pdf_preserves_page_order(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage("Page one"),
                FakePage("Page two"),
                FakePage("Page three"),
            ]
        ),
    )

    result = FileExtractionService().extract_pdf(
        file_name="ordered.pdf",
        content=b"%PDF-test",
    )

    assert result.text == ("Page one\n\n" "Page two\n\n" "Page three")


def test_extract_pdf_normalizes_page_text(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage("\r\n  First line\r\nSecond line  \r\n"),
            ]
        ),
    )

    result = FileExtractionService().extract_pdf(
        file_name="normalized.pdf",
        content=b"%PDF-test",
    )

    assert result.text == "First line\nSecond line"


def test_extract_pdf_ignores_pages_returning_none(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage(None),
                FakePage("Useful text"),
                FakePage(None),
            ]
        ),
    )

    result = FileExtractionService().extract_pdf(
        file_name="mixed.pdf",
        content=b"%PDF-test",
    )

    assert result.text == "Useful text"
    assert result.page_count == 3


def test_extract_pdf_ignores_whitespace_only_pages(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage(" "),
                FakePage("\r\n\t"),
                FakePage("Useful text"),
            ]
        ),
    )

    result = FileExtractionService().extract_pdf(
        file_name="mixed.pdf",
        content=b"%PDF-test",
    )

    assert result.text == "Useful text"
    assert result.page_count == 3


def test_extract_pdf_preserves_internal_page_spacing(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage("Column A    Column B"),
            ]
        ),
    )

    result = FileExtractionService().extract_pdf(
        file_name="spacing.pdf",
        content=b"%PDF-test",
    )

    assert result.text == "Column A    Column B"


def test_extract_pdf_records_original_byte_size(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader([FakePage("Text")]),
    )

    content = b"%PDF-original-bytes"

    result = FileExtractionService().extract_pdf(
        file_name="size.pdf",
        content=content,
    )

    assert result.size_bytes == len(content)


def test_extract_pdf_rejects_file_above_configured_limit():
    service = FileExtractionService(
        max_upload_size_bytes=4,
    )

    with pytest.raises(
        FileTooLargeError,
        match="maximum allowed size",
    ):
        service.extract_pdf(
            file_name="large.pdf",
            content=b"12345",
        )


@pytest.mark.parametrize(
    "file_name",
    [
        "report.txt",
        "report.docx",
        "report",
        "report.pdf.txt",
        ".pdf.backup",
    ],
)
def test_extract_pdf_rejects_non_pdf_file_name(file_name):
    service = FileExtractionService()

    with pytest.raises(
        UnsupportedFileTypeError,
        match=r"Expected a \.pdf file",
    ):
        service.extract_pdf(
            file_name=file_name,
            content=b"%PDF-test",
        )


@pytest.mark.parametrize(
    "file_name",
    [
        "",
        " ",
        "\t",
        "\r\n",
    ],
)
def test_extract_pdf_rejects_blank_file_name(file_name):
    service = FileExtractionService()

    with pytest.raises(
        UnsupportedFileTypeError,
        match="supported file name",
    ):
        service.extract_pdf(
            file_name=file_name,
            content=b"%PDF-test",
        )


@pytest.mark.parametrize(
    "file_name",
    [
        None,
        123,
        b"report.pdf",
    ],
)
def test_extract_pdf_rejects_non_string_file_name(file_name):
    service = FileExtractionService()

    with pytest.raises(
        TypeError,
        match="file_name must be a string",
    ):
        service.extract_pdf(
            file_name=file_name,
            content=b"%PDF-test",
        )


@pytest.mark.parametrize(
    "content",
    [
        "PDF",
        bytearray(b"PDF"),
        memoryview(b"PDF"),
        None,
    ],
)
def test_extract_pdf_rejects_non_bytes_content(content):
    service = FileExtractionService()

    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        service.extract_pdf(
            file_name="report.pdf",
            content=content,
        )


def test_extract_pdf_rejects_invalid_pdf_bytes():
    service = FileExtractionService()

    with pytest.raises(
        InvalidPdfError,
        match="could not be read",
    ):
        service.extract_pdf(
            file_name="invalid.pdf",
            content=b"This is not a PDF.",
        )


def test_extract_pdf_rejects_real_blank_pdf():
    service = FileExtractionService()

    with pytest.raises(
        EmptyExtractedTextError,
        match="does not contain extractable text",
    ):
        service.extract_pdf(
            file_name="blank.pdf",
            content=make_blank_pdf(),
        )


def test_extract_pdf_reports_real_pdf_page_count_before_empty_rejection(
    monkeypatch,
):
    reader = FakeReader(
        [
            FakePage("Page one"),
            FakePage("Page two"),
        ]
    )

    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: reader,
    )

    result = FileExtractionService().extract_pdf(
        file_name="pages.pdf",
        content=b"%PDF-test",
    )

    assert result.page_count == 2


def test_extract_pdf_rejects_encrypted_pdf():
    service = FileExtractionService()

    with pytest.raises(
        EncryptedPdfError,
        match="Encrypted PDF files are not supported",
    ):
        service.extract_pdf(
            file_name="encrypted.pdf",
            content=make_blank_pdf(
                encrypted=True,
            ),
        )


def test_extract_pdf_rejects_reader_marked_encrypted(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [],
            encrypted=True,
        ),
    )

    with pytest.raises(
        EncryptedPdfError,
        match="Encrypted PDF files are not supported",
    ):
        FileExtractionService().extract_pdf(
            file_name="encrypted.pdf",
            content=b"%PDF-test",
        )


def test_extract_pdf_rejects_document_with_no_usable_text(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage(None),
                FakePage(" "),
                FakePage("\r\n\t"),
            ]
        ),
    )

    with pytest.raises(
        EmptyExtractedTextError,
        match="does not contain extractable text",
    ):
        FileExtractionService().extract_pdf(
            file_name="image-only.pdf",
            content=b"%PDF-test",
        )


def test_extract_pdf_fails_closed_when_page_extraction_fails(
    monkeypatch,
):
    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader(
            [
                FakePage("First page"),
                FailingPage(),
                FakePage("Third page"),
            ]
        ),
    )

    with pytest.raises(
        InvalidPdfError,
        match="could not be read",
    ) as error:
        FileExtractionService().extract_pdf(
            file_name="broken-page.pdf",
            content=b"%PDF-test",
        )

    assert "private parser failure" not in str(error.value)


def test_extract_pdf_does_not_expose_parser_exception(
    monkeypatch,
):
    def fail_reader(*args, **kwargs):
        raise ValueError("sensitive internal parser diagnostic")

    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        fail_reader,
    )

    with pytest.raises(
        InvalidPdfError,
        match="could not be read",
    ) as error:
        FileExtractionService().extract_pdf(
            file_name="broken.pdf",
            content=b"%PDF-test",
        )

    assert "sensitive internal parser diagnostic" not in str(error.value)


def test_extract_pdf_does_not_require_provider_configuration(
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

    monkeypatch.setattr(
        file_extraction,
        "PdfReader",
        lambda *args, **kwargs: FakeReader([FakePage("Offline PDF extraction.")]),
    )

    result = FileExtractionService().extract_pdf(
        file_name="offline.pdf",
        content=b"%PDF-test",
    )

    assert result.text == "Offline PDF extraction."


def test_pdf_extraction_does_not_modify_txt_behavior():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="notes.txt",
        content=b"Existing TXT behavior.",
    )

    assert result.text == "Existing TXT behavior."
    assert result.file_type is FileType.TXT
    assert result.page_count is None
