from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from starlette.requests import Request

from app.db.database import SessionLocal
from app.db.models import Summary

router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)

@router.get("/history")
def history(request: Request):

    db = SessionLocal()

    rows = (
        db.query(Summary)
        .order_by(Summary.id.desc())
        .all()
    )

    db.close()

    summaries = []

    for row in rows:

        summaries.append(
            {
                "original_text":
                    row.original_text,

                "summary":
                    row.summary,

                "content_type":
                    row.content_type
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "summaries": summaries
        }
    )