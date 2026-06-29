from fastapi import APIRouter

router = APIRouter()


runtime_cache = {}


@router.get(
    "/execution"
)
def execution():

    return runtime_cache