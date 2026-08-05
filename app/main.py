from fastapi import (
    FastAPI,
)

from app.api.v1.summarize_endpoint import (
    router,
)

from app.routes.ai import router as ai_router

from app.api.metrics import router as metrics_router

from app.api.v1.execution_playground import router as playground_router

app = FastAPI()

app.include_router(metrics_router)

app.include_router(router)

app.include_router(playground_router, prefix="/playground", tags=["playground"])

app.include_router(ai_router, prefix="/api/v1", tags=["AI"])
