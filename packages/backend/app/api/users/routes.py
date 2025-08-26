from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class PlacehodlerResponse(BaseModel):
    message: str


@router.get("", response_model=PlacehodlerResponse)
async def placeholder() -> Any:
    return {"message": "This is a placeholder for user routes."}
