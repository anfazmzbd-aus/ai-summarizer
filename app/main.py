from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.home import router as home_router
from app.routes.summarize import router as summarize_router
from app.routes.history import router as history_router
from app.routes.upload import router as upload_router
from app.routes.dashboard import router as dashboard_router
from app.db.database import Base, engine

from fastapi.staticfiles import StaticFiles

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="AI Summarizer",
    version="1.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home_router)
app.include_router(summarize_router)
app.include_router(history_router)
app.include_router(upload_router)
app.include_router(dashboard_router)