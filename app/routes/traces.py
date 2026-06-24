from fastapi import APIRouter
from app.services.logging.trace_logger import (
    trace_logger
)

router = APIRouter()


@router.get(
    "/traces"
)
def traces():

    clean = []

    for t in trace_logger.get_traces():

        item = t.copy()

        item.pop(
            "start",
            None
        )

        item.pop(
            "end",
            None
        )

        clean.append(
            item
        )

    return {
        "traces":
            clean
    }
