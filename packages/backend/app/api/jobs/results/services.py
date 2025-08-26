from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.results.models import PublicJobResultsResponse
from app.db.models import Job, JobStatus


async def get_public_results(
    db: AsyncSession, shareable_id: UUID
) -> PublicJobResultsResponse:
    result = await db.execute(
        select(Job).where(and_(Job.shareable_id == shareable_id, Job.is_public))
    )
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared job not found or not public",
        )

    if job.status != JobStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is not completed",
        )

    # TODO: Implement actual transformation service integration
    return PublicJobResultsResponse(
        shareable_id=job.shareable_id,
        job_type=job.job_type,
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
