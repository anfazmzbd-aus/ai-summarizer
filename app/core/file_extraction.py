from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from io import BytesIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError


MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class FileType(str, Enum):
    TXT = "txt"
    PDF = "pdf"


class FileExtractionError(ValueError):
    """Base error for product-safe file extraction failures."""


class UnsupportedFileTypeError(FileExtractionError):
    """Raised when the requested file type is not supported."""


class FileTooLargeError(FileExtractionError):
    """Raised when an uploaded file exceeds the product size limit."""


class InvalidTextEncodingError(FileExtractionError):
    """Raised when a text file cannot be decoded using the supported encoding."""


class InvalidPdfError(FileExtractionError):
    """Raised when PDF content cannot be safely parsed."""


class EncryptedPdfError(FileExtractionError):
    """Raised when a PDF requires decryption before text extraction."""


class EmptyExtractedTextError(FileExtractionError):
    """Raised when a file contains no usable text after normalization."""


@dataclass(frozen=True, slots=True)
class FileExtractionResult:
    text: str
    file_name: str
    file_type: FileType
    size_bytes: int
    page_count: int | None = None


def normalize_extracted_text(text: str) -> str:
    """
    Normalize extracted document text without changing its semantic content.

    Line endings are converted to LF and outer whitespace is removed.
    Internal whitespace and paragraph structure are otherwise preserved.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return normalized.strip()


class FileExtractionService:
    """
    Product file-extraction boundary.

    Supports UTF-8 TXT and text-extractable PDF documents.

    This service performs extraction only. It does not persist files,
    construct prompts, invoke providers, or perform summarization.
    """

    def __init__(
        self,
        *,
        max_upload_size_bytes: int = MAX_UPLOAD_SIZE_BYTES,
    ) -> None:
        if (
            not isinstance(max_upload_size_bytes, int)
            or isinstance(max_upload_size_bytes, bool)
            or max_upload_size_bytes <= 0
        ):
            raise ValueError("max_upload_size_bytes must be a positive integer")

        self._max_upload_size_bytes = max_upload_size_bytes

    @property
    def max_upload_size_bytes(self) -> int:
        return self._max_upload_size_bytes

    def extract_txt(
        self,
        *,
        file_name: str,
        content: bytes,
    ) -> FileExtractionResult:
        """
        Extract normalized UTF-8 text from a TXT document.

        UTF-8 BOM input is accepted through utf-8-sig decoding. Other
        encodings are intentionally rejected rather than guessed.
        """
        normalized_file_name = self._validate_file_name(
            file_name,
            expected_type=FileType.TXT,
        )
        self._validate_content(content)

        try:
            decoded = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise InvalidTextEncodingError(
                "Text files must use UTF-8 encoding."
            ) from exc

        text = normalize_extracted_text(decoded)

        if not text:
            raise EmptyExtractedTextError("The text file does not contain usable text.")

        return FileExtractionResult(
            text=text,
            file_name=normalized_file_name,
            file_type=FileType.TXT,
            size_bytes=len(content),
            page_count=None,
        )

    def extract_pdf(
        self,
        *,
        file_name: str,
        content: bytes,
    ) -> FileExtractionResult:
        """
        Extract normalized text from a PDF document.

        Pages are processed in document order. Pages without extractable text
        are ignored. Encrypted documents and PDFs with no usable text are
        rejected with product-safe domain errors.
        """
        normalized_file_name = self._validate_file_name(
            file_name,
            expected_type=FileType.PDF,
        )
        self._validate_content(content)

        try:
            reader = PdfReader(
                BytesIO(content),
                strict=False,
            )
        except (PdfReadError, ValueError, TypeError, OSError) as exc:
            raise InvalidPdfError("The PDF file could not be read.") from exc

        try:
            if reader.is_encrypted:
                raise EncryptedPdfError("Encrypted PDF files are not supported.")

            page_count = len(reader.pages)
            page_texts: list[str] = []

            for page in reader.pages:
                try:
                    extracted = page.extract_text()
                except Exception as exc:
                    raise InvalidPdfError("The PDF file could not be read.") from exc

                if extracted is None:
                    continue

                normalized_page = normalize_extracted_text(extracted)

                if normalized_page:
                    page_texts.append(normalized_page)

        except EncryptedPdfError:
            raise
        except (PdfReadError, ValueError, TypeError, OSError) as exc:
            raise InvalidPdfError("The PDF file could not be read.") from exc

        text = "\n\n".join(page_texts)

        if not text:
            raise EmptyExtractedTextError(
                "The PDF file does not contain extractable text."
            )

        return FileExtractionResult(
            text=text,
            file_name=normalized_file_name,
            file_type=FileType.PDF,
            size_bytes=len(content),
            page_count=page_count,
        )

    def _validate_content(self, content: bytes) -> None:
        if not isinstance(content, bytes):
            raise TypeError("content must be bytes")

        if len(content) > self._max_upload_size_bytes:
            raise FileTooLargeError(
                "The uploaded file exceeds the maximum allowed size."
            )

    @staticmethod
    def _validate_file_name(
        file_name: str,
        *,
        expected_type: FileType,
    ) -> str:
        if not isinstance(file_name, str):
            raise TypeError("file_name must be a string")

        normalized = file_name.strip()

        if not normalized:
            raise UnsupportedFileTypeError("A supported file name is required.")

        expected_suffix = f".{expected_type.value}"

        if not normalized.lower().endswith(expected_suffix):
            raise UnsupportedFileTypeError(f"Expected a {expected_suffix} file.")

        return normalized
