from fastapi import APIRouter

from app.api.utils.routes import router as utils_router

v1_router = APIRouter()
v1_router.include_router(utils_router)
