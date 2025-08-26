from typing import Any

from fastapi import APIRouter

from .models import HealthCheckResponse

router = APIRouter()


@router.get("/health-check", response_model=HealthCheckResponse)
async def health_check() -> Any:
    return HealthCheckResponse(status="ok")
