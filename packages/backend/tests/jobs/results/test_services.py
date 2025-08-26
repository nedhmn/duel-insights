import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.results.services import get_public_results
from app.db.models import Job, JobStatus, JobType, User


class TestResultsServices:
    @pytest.fixture
    async def sample_user(self, test_db_session: AsyncSession) -> User:
        user = User(clerk_user_id="user_123")
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        return user

    @pytest.fixture
    async def public_job(self, test_db_session: AsyncSession, sample_user: User) -> Job:
        job = Job(
            job_type=JobType.INDIVIDUAL,
            status=JobStatus.COMPLETED,
            user_id=sample_user.id,
            urls=["https://example.com/game1"],
            total_urls=1,
            is_public=True,
        )
        test_db_session.add(job)
        await test_db_session.commit()
        await test_db_session.refresh(job)
        return job

    async def test_get_public_results_success(
        self, public_job: Job, test_db_session: AsyncSession
    ) -> None:
        result = await get_public_results(test_db_session, public_job.shareable_id)

        assert result.shareable_id == public_job.shareable_id
        assert result.job_type == public_job.job_type
        assert result.summary is not None
        assert result.detailed_results is not None

    async def test_get_public_results_not_public(
        self, test_db_session: AsyncSession, sample_user: User
    ) -> None:
        private_job = Job(
            job_type=JobType.INDIVIDUAL,
            status=JobStatus.COMPLETED,
            user_id=sample_user.id,
            urls=["https://example.com/game1"],
            total_urls=1,
            is_public=False,
        )
        test_db_session.add(private_job)
        await test_db_session.commit()
        await test_db_session.refresh(private_job)

        with pytest.raises(HTTPException) as exc_info:
            await get_public_results(test_db_session, private_job.shareable_id)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_public_results_not_completed(
        self, test_db_session: AsyncSession, sample_user: User
    ) -> None:
        incomplete_job = Job(
            job_type=JobType.INDIVIDUAL,
            status=JobStatus.PENDING,
            user_id=sample_user.id,
            urls=["https://example.com/game1"],
            total_urls=1,
            is_public=True,
        )
        test_db_session.add(incomplete_job)
        await test_db_session.commit()
        await test_db_session.refresh(incomplete_job)

        with pytest.raises(HTTPException) as exc_info:
            await get_public_results(test_db_session, incomplete_job.shareable_id)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
