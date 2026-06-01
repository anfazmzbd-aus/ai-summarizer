import json

from app.db.database import SessionLocal
from app.db.models import Summary


def save_summary(
    text: str,
    result: dict
):

    db = SessionLocal()

    try:
        db_summary = Summary(
            original_text=text,
            summary=result.get("summary", ""),
            content_type=result.get("content_type", "General Content"),

            agent_output=json.dumps({
                "actions": result.get("actions", []),
                "insights": result.get("insights", []),
                "findings": result.get("findings", []),
                "plan": result.get("plan", {})
            })
        )

        db.add(db_summary)
        db.commit()

    finally:
        db.close()