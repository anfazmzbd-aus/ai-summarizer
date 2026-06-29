import json

from collections import Counter

from app.db.database import SessionLocal
from app.db.models import Summary


def get_agent_usage():

    db = SessionLocal()

    rows = db.query(
        Summary
    ).all()

    counter = Counter()

    for row in rows:

        data = json.loads(
            row.agent_output
        )

        execution = data.get(
            "execution",
            {}
        )

        for agent in execution.get(
            "agents_executed",
            []
        ):
            counter[agent] += 1

    db.close()

    return dict(counter)