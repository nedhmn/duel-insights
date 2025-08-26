from fastapi import APIRouter

from app.api.users.routes import router as users_router
from app.api.utils.routes import router as utils_router

v1_router = APIRouter()
v1_router.include_router(utils_router, prefix="/utils", tags=["utils"])
v1_router.include_router(users_router, prefix="/users/me", tags=["users"])
