from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.models import JobResponse
from app.db.models import Job, JobStatus, JobType, User


async def create_individual_job(
    db: AsyncSession, urls: list[HttpUrl], user: User
) -> JobResponse:
    url_strings = [str(url) for url in urls]

    job = Job(
        job_type=JobType.INDIVIDUAL,
        status=JobStatus.PENDING,
        user_id=user.id,
        urls=url_strings,
        total_urls=len(url_strings),
        processed_urls=0,
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

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
