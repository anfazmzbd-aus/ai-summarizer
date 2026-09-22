from __future__ import annotations

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
    status,
)

from app.api.file_extraction_schemas import (
    ExtractedFileMetadata,
    FileExtractionResponse,
)
from app.core.file_extraction import (
    EmptyExtractedTextError,
    EncryptedPdfError,
    FileExtractionService,
    FileTooLargeError,
    InvalidPdfError,
    InvalidTextEncodingError,
    UnsupportedFileTypeError,
)

router = APIRouter(
    prefix="/api/v1/files",
    tags=["files"],
)

_file_extraction_service = FileExtractionService()

_SUPPORTED_CONTENT_TYPES = {
    ".txt": "text/plain",
    ".pdf": "application/pdf",
}


@router.post(
    "/extract",
    response_model=FileExtractionResponse,
)
async def extract_file(
    file: list[UploadFile] = File(...),
) -> FileExtractionResponse:
    """
    Extract product-safe normalized text from exactly one supported document.

    Extraction is intentionally independent from summarization. The returned
    text rejoins the existing source-text workflow before any summarization
    request is made.
    """
    if len(file) != 1:
        await _close_uploads(file)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Upload exactly one file.",
        )

    upload = file[0]
    file_name = upload.filename or ""

    try:
        suffix = _normalized_suffix(file_name)

        if suffix not in _SUPPORTED_CONTENT_TYPES:
            raise UnsupportedFileTypeError("Only TXT and PDF files are supported.")

        _validate_content_type(
            suffix=suffix,
            content_type=upload.content_type,
        )

        content = await _read_upload_with_limit(
            upload,
            max_bytes=_file_extraction_service.max_upload_size_bytes,
        )

        if suffix == ".txt":
            result = _file_extraction_service.extract_txt(
                file_name=file_name,
                content=content,
            )
        else:
            result = _file_extraction_service.extract_pdf(
                file_name=file_name,
                content=content,
            )

    except FileTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=str(exc),
        ) from exc
    except InvalidTextEncodingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except EncryptedPdfError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except EmptyExtractedTextError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except InvalidPdfError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    finally:
        await upload.close()

    return FileExtractionResponse(
        text=result.text,
        file=ExtractedFileMetadata(
            name=result.file_name,
            type=result.file_type,
            size_bytes=result.size_bytes,
            page_count=result.page_count,
        ),
    )


async def _read_upload_with_limit(
    file: UploadFile,
    *,
    max_bytes: int,
) -> bytes:
    content = await file.read(max_bytes + 1)

    if len(content) > max_bytes:
        raise FileTooLargeError("The uploaded file exceeds the maximum allowed size.")

    return content


async def _close_uploads(
    files: list[UploadFile],
) -> None:
    for upload in files:
        await upload.close()


def _normalized_suffix(file_name: str) -> str:
    if not isinstance(file_name, str):
        return ""

    normalized = file_name.strip().lower()

    if normalized.endswith(".txt"):
        return ".txt"

    if normalized.endswith(".pdf"):
        return ".pdf"

    return ""


def _normalized_content_type(
    content_type: str | None,
) -> str:
    if not content_type:
        return ""

    return (
        content_type.split(
            ";",
            1,
        )[0]
        .strip()
        .lower()
    )


def _validate_content_type(
    *,
    suffix: str,
    content_type: str | None,
) -> None:
    normalized_content_type = _normalized_content_type(content_type)

    expected_content_type = _SUPPORTED_CONTENT_TYPES.get(suffix)

    if (
        not normalized_content_type
        or expected_content_type is None
        or normalized_content_type != expected_content_type
    ):
        raise UnsupportedFileTypeError(
            "The uploaded file content type is not supported."
        )
