from fastapi import APIRouter

from app.api.jobs.individual.routes import router as jobs_individual_router
from app.api.jobs.results.routes import router as jobs_results_router
from app.api.jobs.routes import router as jobs_router
from app.api.users.routes import router as users_router
from app.api.utils.routes import router as utils_router

v1_router = APIRouter()
v1_router.include_router(utils_router, prefix="/utils", tags=["utils"])
v1_router.include_router(users_router, prefix="/users/me", tags=["users"])
v1_router.include_router(
    jobs_individual_router, prefix="/jobs/individual", tags=["individual"]
)
v1_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
v1_router.include_router(jobs_results_router, prefix="/jobs/results", tags=["results"])
