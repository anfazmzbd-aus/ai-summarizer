from fastapi import (
    FastAPI,
)

from app.api.v1.summarize_endpoint import (
    router,
)

from app.routes.ai import router as ai_router

from app.api.metrics import router as metrics_router

from app.api.v1.execution_playground import router as playground_router
from app.routes.frontend import router as frontend_router
from fastapi.staticfiles import StaticFiles

from pathlib import Path


_STATIC_PATH = Path(__file__).resolve().parents[1] / "static"

app = FastAPI()

app.mount("/static", StaticFiles(directory=_STATIC_PATH), name="static")

app.include_router(metrics_router)

app.include_router(router)

app.include_router(playground_router, prefix="/playground", tags=["playground"])

app.include_router(ai_router)

app.include_router(frontend_router)
