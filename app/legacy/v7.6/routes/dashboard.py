from fastapi import APIRouter
from app.services.db_service import (
    get_statistics
)

router = APIRouter()

@router.get("/dashboard")
def dashboard():

    return get_statistics()