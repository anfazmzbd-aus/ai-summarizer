from __future__ import annotations

from pydantic import BaseModel

from app.core.file_extraction import FileType


class ExtractedFileMetadata(BaseModel):
    name: str
    type: FileType
    size_bytes: int
    page_count: int | None = None


class FileExtractionResponse(BaseModel):
    text: str
    file: ExtractedFileMetadata


class FileExtractionErrorResponse(BaseModel):
    detail: str
