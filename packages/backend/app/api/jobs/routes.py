from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import DBDep, UserDep
from app.api.jobs.models import (
    JobListResponse,
    JobResponse,
    JobResultsResponse,
    JobShareRequest,
    JobShareResponse,
)
from app.api.jobs.services import (
    cancel_job,
    enable_sharing,
    get_job_by_id,
    get_job_progress,
    get_job_results,
    list_user_jobs,
)
from app.db.models import JobStatus, JobType

router = APIRouter()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: UUID,
    current_user: UserDep,
    db: DBDep,
) -> JobResponse:
    return await get_job_by_id(db, job_id, current_user)


@router.get("/{job_id}/progress")
async def get_job_progress_endpoint(
    job_id: UUID,
    current_user: UserDep,
    db: DBDep,
) -> dict[str, Any]:
    return await get_job_progress(db, job_id, current_user)


@router.get("/{job_id}/results", response_model=JobResultsResponse)
async def get_job_results_endpoint(
    job_id: UUID,
    current_user: UserDep,
    db: DBDep,
) -> JobResultsResponse:
    return await get_job_results(db, job_id, current_user)


@router.delete("/{job_id}")
async def cancel_job_endpoint(
    job_id: UUID,
    current_user: UserDep,
    db: DBDep,
) -> dict[str, str]:
    return await cancel_job(db, job_id, current_user)


@router.post("/{job_id}/share", response_model=JobShareResponse)
async def toggle_job_sharing(
    job_id: UUID,
    request: JobShareRequest,
    current_user: UserDep,
    db: DBDep,
) -> JobShareResponse:
    return await enable_sharing(db, job_id, current_user, request.is_public)


@router.get("/", response_model=JobListResponse)
async def list_user_jobs_endpoint(
    current_user: UserDep,
    db: DBDep,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: JobStatus | None = Query(None),
    job_type: JobType | None = Query(None),
) -> JobListResponse:
    return await list_user_jobs(db, current_user, page, per_page, status, job_type)
