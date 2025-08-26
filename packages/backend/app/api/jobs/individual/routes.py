from fastapi import APIRouter, status

from app.api.deps import DBDep, UserDep
from app.api.jobs.individual.models import JobSubmissionRequest
from app.api.jobs.individual.services import create_individual_job
from app.api.jobs.models import JobResponse

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def submit_individual_job(
    request: JobSubmissionRequest,
    current_user: UserDep,
    db: DBDep,
) -> JobResponse:
    return await create_individual_job(db, request.urls, current_user)
