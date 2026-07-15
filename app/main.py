from fastapi import (
    FastAPI,
)

from app.api.v1.summarize_endpoint import (
    router,
)

from app.api.v1.execution_playground import router as playground_router

app = FastAPI()

app.include_router(router)

app.include_router(playground_router, prefix="/playground", tags=["playground"])
