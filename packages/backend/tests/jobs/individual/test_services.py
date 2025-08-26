import pytest
from pydantic import HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.individual.services import create_individual_job
from app.api.jobs.models import JobResponse
from app.db.models import Job, JobStatus, JobType, User


class TestIndividualServices:
    @pytest.fixture
    async def sample_user(self, test_db_session: AsyncSession) -> User:
        user = User(clerk_user_id="user_123")
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        return user

    async def test_create_individual_job_success(
        self, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        urls = [
            HttpUrl("https://example.com/game1"),
            HttpUrl("https://example.com/game2"),
        ]

        result = await create_individual_job(test_db_session, urls, sample_user)

        assert isinstance(result, JobResponse)
        assert result.job_type == JobType.INDIVIDUAL
        assert result.status == JobStatus.PENDING
        assert result.total_urls == 2
        assert result.processed_urls == 0

        # Verify job was saved to database
        db_result = await test_db_session.execute(
            select(Job).where(Job.id == result.job_id)
        )
        job = db_result.scalar_one()
        assert job.urls == ["https://example.com/game1", "https://example.com/game2"]
