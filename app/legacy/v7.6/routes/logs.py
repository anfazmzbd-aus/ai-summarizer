from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.get("/logs")
def logs():

    with open(
        "logs/agent_system.log",
        "r",
        encoding="utf-8"
    ) as f:

        return PlainTextResponse(
            f.read()
        )