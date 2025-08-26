from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.models import JobResponse, JobResultsResponse
from app.api.jobs.models import JobListResponse, JobShareResponse
from app.db.models import Job, JobStatus, JobType, User


async def get_job_by_id(db: AsyncSession, job_id: UUID, user: User) -> JobResponse:
    job = await _get_user_job(db, job_id, user.id)
    return _job_to_response(job)


async def get_job_progress(
    db: AsyncSession, job_id: UUID, user: User
) -> dict[str, Any]:
    from app.api.jobs.models import JobProgressResponse

    job = await _get_user_job(db, job_id, user.id)
    progress = (job.processed_urls / job.total_urls * 100) if job.total_urls > 0 else 0

    return JobProgressResponse(
        job_id=job.id,
        status=job.status,
        processed=job.processed_urls,
        total=job.total_urls,
        progress_percentage=round(progress, 2),
        error_message=job.error_message,
    ).model_dump()


async def get_job_results(
    db: AsyncSession, job_id: UUID, user: User
) -> JobResultsResponse:
    job = await _get_user_job(db, job_id, user.id)

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job is not completed. Current status: {job.status}",
        )

    # TODO: Implement actual transformation service integration
    return JobResultsResponse(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status,
        summary={
            "total_games": len(job.urls),
            "processed_games": job.processed_urls,
            "placeholder": "This will be replaced with actual analysis results",
        },
        detailed_results={
            "games": [
                {"url": url, "status": "processed", "data": "placeholder"}
                for url in job.urls
            ],
            "player_stats": {"placeholder": "Player analysis will go here"},
        },
        generated_at=datetime.utcnow(),
    )


async def cancel_job(db: AsyncSession, job_id: UUID, user: User) -> dict[str, str]:
    job = await _get_user_job(db, job_id, user.id)

    if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel job with status: {job.status}",
        )

    job.status = JobStatus.CANCELLED
    job.error_message = "Job cancelled by user"
    await db.commit()

    return {"status": "cancelled"}


async def list_user_jobs(
    db: AsyncSession,
    user: User,
    page: int = 1,
    per_page: int = 20,
    status_filter: JobStatus | None = None,
    job_type_filter: JobType | None = None,
) -> JobListResponse:
    if per_page > 100:
        per_page = 100

    offset = (page - 1) * per_page

    query = select(Job).where(Job.user_id == user.id)

    if status_filter:
        query = query.where(Job.status == status_filter)

    if job_type_filter:
        query = query.where(Job.job_type == job_type_filter)

    count_query = select(Job.id).where(Job.user_id == user.id)
    if status_filter:
        count_query = count_query.where(Job.status == status_filter)
    if job_type_filter:
        count_query = count_query.where(Job.job_type == job_type_filter)

    total_result = await db.execute(count_query)
    total = len(total_result.all())

    query = query.order_by(desc(Job.created_at)).offset(offset).limit(per_page)
    result = await db.execute(query)
    jobs = result.scalars().all()

    total_pages = (total + per_page - 1) // per_page

    return JobListResponse(
        jobs=[_job_to_response(job).model_dump() for job in jobs],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


async def enable_sharing(
    db: AsyncSession, job_id: UUID, user: User, is_public: bool
) -> JobShareResponse:
    job = await _get_user_job(db, job_id, user.id)

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed jobs can be shared",
        )

    job.is_public = is_public
    await db.commit()

    share_url = f"/results/{job.shareable_id}" if is_public else ""

    return JobShareResponse(
        job_id=job.id,
        shareable_id=job.shareable_id,
        is_public=is_public,
        share_url=share_url,
    )


async def _get_user_job(db: AsyncSession, job_id: UUID, user_id: UUID) -> Job:
    result = await db.execute(
        select(Job).where(and_(Job.id == job_id, Job.user_id == user_id))
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


def _job_to_response(job: Job) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        status=job.status,
        job_type=job.job_type,
        total_urls=job.total_urls,
        processed_urls=job.processed_urls,
        error_message=job.error_message,
        shareable_id=job.shareable_id if job.is_public else None,
        is_public=job.is_public,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )
