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
                "plan": result.get("plan", {}),
                "execution": result.get("execution", {})
            })
        )

        db.add(db_summary)
        db.commit()

    finally:
        db.close()

def get_all_summaries():

    db = SessionLocal()

    try:

        return (
            db.query(Summary)
            .order_by(
                Summary.created_at.desc()
            )
            .all()
        )

    finally:

        db.close()

def get_statistics():

    db = SessionLocal()

    try:

        summaries = db.query(
            Summary
        ).all()

        total_runs = len(
            summaries
        )

        return {
            "total_runs": total_runs,
            "avg_agent_count": "",
            "avg_execution_time": "",
            "most_common_intent": "meeting_notes"
        }

    finally:

        db.close()

