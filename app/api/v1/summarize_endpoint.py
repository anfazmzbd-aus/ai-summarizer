from fastapi import (
    APIRouter,
)

from pydantic import (
    BaseModel,
)

from app.services.summarize_service import (
    SummarizeService,
)

router = APIRouter()


class Request(
    BaseModel,
):

    text: str


@router.post(
    "/summarize"
)
def summarize(
    req: Request,
):

    service = (
        SummarizeService()
    )

    result = (
        service.run(
            req.text
        )
    )

    return result.outputs