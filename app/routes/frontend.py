"""Supported V11 frontend entry point."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse


_TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "templates" / "index.html"

router = APIRouter(tags=["frontend"])


@router.get("/", response_class=FileResponse)
def frontend() -> FileResponse:
    """Serve the supported V11 summarization frontend."""

    return FileResponse(_TEMPLATE_PATH, media_type="text/html")
