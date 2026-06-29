from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

from starlette.requests import Request

from app.db.database import SessionLocal
from app.db.models import Summary
import json

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

        output = {}

        try:
            output = json.loads(
                row.agent_output or "{}"
            )

        except Exception:
            output = {}

        summaries.append(
            {
                "original_text":
                    row.original_text,

                "summary":
                    row.summary,

                "content_type":
                    row.content_type,

                "actions":
                    output.get("actions", []),

                "insights":
                    output.get("insights", []),

                "findings":
                    output.get("findings", []),

                "trends":
                    output.get("trends", []),

                "sentiment":
                    output.get("sentiment", []),

                "risk":
                    output.get("risk", []),

                "root_causes":
                    output.get("root_causes", []),

                "forecasts":
                    output.get("forecasts", []),

                "recommendations":
                    output.get("recommendations", []),

                "plan":
                    json.dumps(
                        json.loads(
                            row.execution_plan
                        )
                        if row.execution_plan
                        else {},
                        indent=2,
                        ensure_ascii=False
                    ),

                "execution":
                    json.dumps(
                        json.loads(
                            row.execution_metadata
                        )
                        if row.execution_metadata
                        else {},
                        indent=2,
                        ensure_ascii=False
                    ),

                "created_at":
                    row.created_at
            }
        )
    #print(F"HISTORY SUMMARY: {summaries}")
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={
            "summaries": summaries
        }
    )