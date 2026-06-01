from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def home():

    with open(
        "app/templates/index.html",
        encoding="utf-8"
    ) as f:

        return f.read()