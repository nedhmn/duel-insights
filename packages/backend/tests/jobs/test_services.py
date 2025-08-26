import uuid

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.services import (
    cancel_job,
    enable_sharing,
    get_job_by_id,
    get_job_progress,
    get_job_results,
    list_user_jobs,
)
from app.db.models import Job, JobStatus, JobType, User


class TestJobServices:
    @pytest.fixture
    async def sample_user(self, test_db_session: AsyncSession) -> User:
        user = User(clerk_user_id="user_123")
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        return user

    @pytest.fixture
    async def sample_job(self, test_db_session: AsyncSession, sample_user: User) -> Job:
        job = Job(
            job_type=JobType.INDIVIDUAL,
            status=JobStatus.PENDING,
            user_id=sample_user.id,
            urls=["https://example.com/game1", "https://example.com/game2"],
            total_urls=2,
            processed_urls=0,
        )
        test_db_session.add(job)
        await test_db_session.commit()
        await test_db_session.refresh(job)
        return job

    async def test_get_job_by_id_success(
        self, sample_job: Job, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        result = await get_job_by_id(test_db_session, sample_job.id, sample_user)

        assert result.job_id == sample_job.id
        assert result.status == sample_job.status
        assert result.job_type == sample_job.job_type

    async def test_get_job_by_id_not_found(
        self, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        non_existent_id = uuid.uuid4()

        with pytest.raises(HTTPException) as exc_info:
            await get_job_by_id(test_db_session, non_existent_id, sample_user)

        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_job_progress(
        self, sample_job: Job, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        result = await get_job_progress(test_db_session, sample_job.id, sample_user)

        assert result["job_id"] == str(sample_job.id)
        assert result["status"] == sample_job.status
        assert result["processed"] == 0
        assert result["total"] == 2
        assert result["progress_percentage"] == 0.0

    async def test_get_job_results_not_completed(
        self, sample_job: Job, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await get_job_results(test_db_session, sample_job.id, sample_user)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
        assert "not completed" in exc_info.value.detail

    async def test_get_job_results_completed(
        self,
        sample_job: Job,
        sample_user: User,
        test_db_session: AsyncSession,
    ) -> None:
        sample_job.status = JobStatus.COMPLETED
        await test_db_session.commit()

        result = await get_job_results(test_db_session, sample_job.id, sample_user)

        assert result.job_id == sample_job.id
        assert result.status == JobStatus.COMPLETED
        assert result.summary is not None
        assert result.detailed_results is not None

    async def test_cancel_job_success(
        self,
        sample_job: Job,
        sample_user: User,
        test_db_session: AsyncSession,
    ) -> None:
        result = await cancel_job(test_db_session, sample_job.id, sample_user)

        assert result["status"] == "cancelled"

        # Verify job status was updated
        await test_db_session.refresh(sample_job)
        assert sample_job.status == JobStatus.CANCELLED

    async def test_cancel_job_already_completed(
        self,
        sample_job: Job,
        sample_user: User,
        test_db_session: AsyncSession,
    ) -> None:
        sample_job.status = JobStatus.COMPLETED
        await test_db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            await cancel_job(test_db_session, sample_job.id, sample_user)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST

    async def test_list_user_jobs(
        self, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        # Create multiple jobs
        for i in range(3):
            job = Job(
                job_type=JobType.INDIVIDUAL,
                status=JobStatus.PENDING,
                user_id=sample_user.id,
                urls=[f"https://example.com/game{i}"],
                total_urls=1,
            )
            test_db_session.add(job)

        await test_db_session.commit()

        result = await list_user_jobs(test_db_session, sample_user, page=1, per_page=10)

        assert len(result.jobs) == 3
        assert result.total == 3
        assert result.page == 1
        assert result.per_page == 10

    async def test_enable_sharing_success(
        self,
        sample_job: Job,
        sample_user: User,
        test_db_session: AsyncSession,
    ) -> None:
        sample_job.status = JobStatus.COMPLETED
        await test_db_session.commit()

        result = await enable_sharing(test_db_session, sample_job.id, sample_user, True)

        assert result.is_public is True
        assert result.shareable_id == sample_job.shareable_id

        # Verify job was updated
        await test_db_session.refresh(sample_job)
        assert sample_job.is_public is True

    async def test_enable_sharing_not_completed(
        self, sample_job: Job, sample_user: User, test_db_session: AsyncSession
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await enable_sharing(test_db_session, sample_job.id, sample_user, True)

        assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
