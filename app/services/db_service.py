from email.mime import text
import json

from app.db.database import SessionLocal
from app.db.models import Summary
from sqlalchemy import func
from collections import Counter
from app.services.logging.logger import logger

def save_summary(
    text: str,
    result: dict
):

    db = SessionLocal()

    try:
        db_summary = Summary(
            original_text=text,

            summary=result["summary"],

            content_type=result.get(
                "content_type",
                "General Content"
            ),

            primary_intent=result["plan"].get(
                "primary_intent"
            ),

            agent_count=result["execution"].get(
                "agent_count"
            ),

            execution_time=float(
                result["execution"].get(
                    "total_execution_time", 
                    0
                )
            ),

            execution_plan=json.dumps(
                result["plan"]
            ),

            execution_metadata=json.dumps(
                result["execution"]
            ),

            agent_output=json.dumps(
                result["artifacts"]
            )
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
        total_runs = db.query(
            Summary
        ).count()
        avg_agent_count = (
            db.query(
                func.avg(
                    Summary.agent_count
                )
            ).scalar()
        )
        avg_execution_time = (
            db.query(
                func.avg(
                    Summary.execution_time
                )
            ).scalar()
        )

        intent_counts = (
            db.query(
                Summary.primary_intent,
                func.count()
            )
            .group_by(
                Summary.primary_intent
            )
            .all()
        )
        most_common_intent = None

        if intent_counts:

            most_common_intent = max(
                intent_counts,
                key=lambda x: x[1]
            )[0]

        intent_distribution = {
            intent: count
            for intent,
            count in intent_counts
        }

        agent_counter = Counter()

        rows = db.query(
            Summary.execution_metadata
        ).all()

        for row in rows:

            if not row.execution_metadata:
                continue

            try:

                metadata = json.loads(
                    row.execution_metadata
                )

            except Exception:

                continue

            for agent in metadata.get(
                "agents_executed",
                []
            ):
                agent_counter[agent] += 1

        agent_usage = dict(
            agent_counter
        )

        avg_agent_count = round(
            avg_agent_count or 0,
            2
        )

        avg_execution_time = round(
            avg_execution_time or 0,
            6
        )
        
        logger.debug(f"total_runs: {type(total_runs)}")
        logger.debug(f"avg_agent_count: {type(avg_agent_count)}")
        logger.debug(f"avg_execution_time: {type(avg_execution_time)}")
        logger.debug(f"most_common_intent: {type(most_common_intent)}")
        logger.debug(f"intent_distribution: {type(intent_distribution)}")
        logger.debug(f"agent_usage: {type(agent_usage)}")

        return {
            "total_runs": int(total_runs),
            "avg_agent_count": avg_agent_count,
            "avg_execution_time": avg_execution_time,
            "most_common_intent": most_common_intent,
            "intent_distribution": dict(intent_distribution),
            "agent_usage": dict(agent_usage)
        }

    finally:

        db.close()

