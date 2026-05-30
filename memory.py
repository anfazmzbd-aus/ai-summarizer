from database import SessionLocal
from models import Summary
import json


def fetch_recent_summaries(limit=5):

    db = SessionLocal()

    rows = db.query(Summary)\
        .order_by(Summary.id.desc())\
        .limit(limit)\
        .all()

    db.close()

    memory = []

    for r in rows:
        memory.append({
            "summary": r.summary,
            "type": r.content_type,
            "actions": json.loads(r.actions or "[]")
        })

    return memory