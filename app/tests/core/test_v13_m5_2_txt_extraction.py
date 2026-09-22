from __future__ import annotations

import pytest

from app.core.file_extraction import (
    MAX_UPLOAD_SIZE_BYTES,
    EmptyExtractedTextError,
    FileExtractionResult,
    FileExtractionService,
    FileTooLargeError,
    FileType,
    InvalidTextEncodingError,
    UnsupportedFileTypeError,
    normalize_extracted_text,
)


def test_default_upload_limit_is_ten_mib():
    assert MAX_UPLOAD_SIZE_BYTES == 10 * 1024 * 1024


def test_service_exposes_configured_upload_limit():
    service = FileExtractionService(
        max_upload_size_bytes=1234,
    )

    assert service.max_upload_size_bytes == 1234


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
        True,
        False,
        1.5,
        "1024",
        None,
    ],
)
def test_service_rejects_invalid_upload_limit(value):
    with pytest.raises(
        ValueError,
        match="max_upload_size_bytes must be a positive integer",
    ):
        FileExtractionService(
            max_upload_size_bytes=value,
        )


def test_extract_txt_returns_structured_result():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="notes.txt",
        content=b"Hello from AI Summarizer.",
    )

    assert isinstance(result, FileExtractionResult)
    assert result.text == "Hello from AI Summarizer."
    assert result.file_name == "notes.txt"
    assert result.file_type is FileType.TXT
    assert result.size_bytes == len(b"Hello from AI Summarizer.")
    assert result.page_count is None


def test_extract_txt_accepts_uppercase_extension():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="NOTES.TXT",
        content=b"Supported text.",
    )

    assert result.file_name == "NOTES.TXT"
    assert result.file_type is FileType.TXT


def test_extract_txt_trims_file_name_outer_whitespace():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="  notes.txt  ",
        content=b"Supported text.",
    )

    assert result.file_name == "notes.txt"


def test_extract_txt_accepts_utf8_unicode():
    service = FileExtractionService()

    source = "Résumé\n日本語\nසිංහල"

    result = service.extract_txt(
        file_name="unicode.txt",
        content=source.encode("utf-8"),
    )

    assert result.text == source


def test_extract_txt_accepts_utf8_bom():
    service = FileExtractionService()

    content = b"\xef\xbb\xbfDocument content"

    result = service.extract_txt(
        file_name="bom.txt",
        content=content,
    )

    assert result.text == "Document content"
    assert not result.text.startswith("\ufeff")
    assert result.size_bytes == len(content)


def test_extract_txt_normalizes_windows_line_endings():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="windows.txt",
        content=b"Line one\r\nLine two\r\nLine three",
    )

    assert result.text == "Line one\nLine two\nLine three"


def test_extract_txt_normalizes_legacy_carriage_returns():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="legacy.txt",
        content=b"Line one\rLine two\rLine three",
    )

    assert result.text == "Line one\nLine two\nLine three"


def test_extract_txt_preserves_internal_blank_lines():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="paragraphs.txt",
        content=b"First paragraph.\n\nSecond paragraph.",
    )

    assert result.text == "First paragraph.\n\nSecond paragraph."


def test_extract_txt_preserves_internal_spaces():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="spacing.txt",
        content=b"Column A    Column B",
    )

    assert result.text == "Column A    Column B"


def test_extract_txt_removes_outer_whitespace():
    service = FileExtractionService()

    result = service.extract_txt(
        file_name="trim.txt",
        content=b"\n  Useful content.  \n",
    )

    assert result.text == "Useful content."


def test_extract_txt_records_original_byte_size():
    service = FileExtractionService()

    content = "Résumé".encode("utf-8")

    result = service.extract_txt(
        file_name="size.txt",
        content=content,
    )

    assert result.size_bytes == len(content)


def test_extract_txt_accepts_file_exactly_at_configured_limit():
    service = FileExtractionService(
        max_upload_size_bytes=4,
    )

    result = service.extract_txt(
        file_name="limit.txt",
        content=b"text",
    )

    assert result.text == "text"
    assert result.size_bytes == 4


def test_extract_txt_rejects_file_above_configured_limit():
    service = FileExtractionService(
        max_upload_size_bytes=4,
    )

    with pytest.raises(
        FileTooLargeError,
        match="maximum allowed size",
    ):
        service.extract_txt(
            file_name="large.txt",
            content=b"12345",
        )


def test_extract_txt_rejects_non_utf8_content():
    service = FileExtractionService()

    with pytest.raises(
        InvalidTextEncodingError,
        match="UTF-8",
    ):
        service.extract_txt(
            file_name="invalid.txt",
            content=b"\xff\xfe\xfa",
        )


@pytest.mark.parametrize(
    "content",
    [
        b"",
        b" ",
        b"\n",
        b"\r\n",
        b"\t",
        b" \r\n\t ",
        b"\xef\xbb\xbf",
        b"\xef\xbb\xbf \r\n\t ",
    ],
)
def test_extract_txt_rejects_empty_or_whitespace_only_text(content):
    service = FileExtractionService()

    with pytest.raises(
        EmptyExtractedTextError,
        match="does not contain usable text",
    ):
        service.extract_txt(
            file_name="empty.txt",
            content=content,
        )


@pytest.mark.parametrize(
    "file_name",
    [
        "notes.pdf",
        "notes.docx",
        "notes",
        "notes.txt.pdf",
        ".txt.backup",
    ],
)
def test_extract_txt_rejects_non_txt_file_name(file_name):
    service = FileExtractionService()

    with pytest.raises(
        UnsupportedFileTypeError,
        match=r"Expected a \.txt file",
    ):
        service.extract_txt(
            file_name=file_name,
            content=b"Text",
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
def test_extract_txt_rejects_blank_file_name(file_name):
    service = FileExtractionService()

    with pytest.raises(
        UnsupportedFileTypeError,
        match="supported file name",
    ):
        service.extract_txt(
            file_name=file_name,
            content=b"Text",
        )


@pytest.mark.parametrize(
    "file_name",
    [
        None,
        123,
        b"notes.txt",
    ],
)
def test_extract_txt_rejects_non_string_file_name(file_name):
    service = FileExtractionService()

    with pytest.raises(
        TypeError,
        match="file_name must be a string",
    ):
        service.extract_txt(
            file_name=file_name,
            content=b"Text",
        )


@pytest.mark.parametrize(
    "content",
    [
        "Text",
        bytearray(b"Text"),
        memoryview(b"Text"),
        None,
    ],
)
def test_extract_txt_rejects_non_bytes_content(content):
    service = FileExtractionService()

    with pytest.raises(
        TypeError,
        match="content must be bytes",
    ):
        service.extract_txt(
            file_name="notes.txt",
            content=content,
        )


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("text", "text"),
        ("  text  ", "text"),
        ("\r\ntext\r\n", "text"),
        ("one\r\ntwo", "one\ntwo"),
        ("one\rtwo", "one\ntwo"),
        ("one\n\ntwo", "one\n\ntwo"),
        ("A    B", "A    B"),
    ],
)
def test_normalize_extracted_text(source, expected):
    assert normalize_extracted_text(source) == expected


@pytest.mark.parametrize(
    "value",
    [
        None,
        123,
        b"text",
        [],
    ],
)
def test_normalize_extracted_text_rejects_non_string(value):
    with pytest.raises(
        TypeError,
        match="text must be a string",
    ):
        normalize_extracted_text(value)


def test_result_is_immutable():
    result = FileExtractionResult(
        text="Text",
        file_name="notes.txt",
        file_type=FileType.TXT,
        size_bytes=4,
    )

    with pytest.raises(AttributeError):
        result.text = "Changed"


def test_file_type_has_stable_public_values():
    assert FileType.TXT.value == "txt"
    assert FileType.PDF.value == "pdf"


def test_txt_extraction_does_not_require_provider_configuration(
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

    service = FileExtractionService()

    result = service.extract_txt(
        file_name="offline.txt",
        content=b"Offline extraction.",
    )

    assert result.text == "Offline extraction."
