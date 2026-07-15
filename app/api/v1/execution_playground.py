from fastapi import APIRouter
from pydantic import BaseModel

# from typing import Dict, Any, Optional

from app.services.summarize_service import (
    SummarizeService,
)

from app.orchestration.contracts.execution_response import (
    ExecutionResponse,
)


router = APIRouter()


class PlaygroundRequest(BaseModel):

    text: str

    mode: str = "summary"

    debug: bool = True


@router.get("/")
def playground_home():

    return {
        "name": "Execution Playground",
        "execute": "/playground/execute",
        "docs": "/docs",
    }


@router.post(
    "/execute",
    response_model=ExecutionResponse,
)
def execute_playground(
    req: PlaygroundRequest,
):

    service = SummarizeService()

    execution = service.run(req.text)

    return execution
