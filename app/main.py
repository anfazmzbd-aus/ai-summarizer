from fastapi import (
    FastAPI,
)

from app.api.v1.summarize_endpoint import (
    router,
)

app = FastAPI()

app.include_router(
    router
)