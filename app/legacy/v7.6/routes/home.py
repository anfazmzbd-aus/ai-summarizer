from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.services.logging.logger import logger

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home():

    with open(
        "app/templates/index.html",
        encoding="utf-8"
    ) as f:
        logger.info("==============Serving home page==============")
        logger.info("==============EXECUTION START==============")
        return f.read()