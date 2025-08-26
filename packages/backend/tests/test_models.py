import pytest
import uuid
from datetime import datetime

from app.db.models import User, Job, JobStatus, JobType, ScrapedData, GFWLTeamSubmission


class TestUserModel:
    """Unit tests for User model."""

    @pytest.mark.unit
    def test_user_creation(self) -> None:
        """Test User model creation with required fields."""
        user = User(clerk_user_id="clerk_12345")

        assert user.clerk_user_id == "clerk_12345"
        # Note: id, created_at, updated_at are set by database defaults
        # In unit tests without DB, they will be None until persisted
        assert user.id is None  # Will be set by database
        assert user.created_at is None  # Will be set by database
        assert user.updated_at is None  # Will be set by database

    @pytest.mark.unit
    def test_user_relationships(self) -> None:
        """Test User model relationships."""
        user = User(clerk_user_id="clerk_12345")

        # Test that jobs relationship is initialized as empty list
        assert user.jobs == []
        assert hasattr(user, "jobs")


class TestJobModel:
    """Unit tests for Job model."""

    @pytest.mark.unit
    def test_job_creation_individual(self) -> None:
        """Test Job model creation for individual mode."""
        user_id = uuid.uuid4()
        urls = ["https://example.com/replay1", "https://example.com/replay2"]

        job = Job(
            job_type=JobType.INDIVIDUAL,
            user_id=user_id,
            urls=urls,
            total_urls=len(urls),
        )

        assert job.job_type == JobType.INDIVIDUAL
        assert job.status is None  # Will be set by database default
        assert job.user_id == user_id
        assert job.urls == urls
        assert job.total_urls == 2
        assert job.processed_urls is None  # Will be set by database default
        assert job.team_data is None
        assert job.error_message is None
        assert job.shareable_id is None  # Will be set by database default
        assert job.is_public is None  # Will be set by database default
        assert job.started_at is None
        assert job.completed_at is None

    @pytest.mark.unit
    def test_job_creation_gfwl(self) -> None:
        """Test Job model creation for GFWL mode."""
        user_id = uuid.uuid4()
        urls = ["https://example.com/match1", "https://example.com/match2"]
        team_data = {"team_name": "Test Team", "week": 1}

        job = Job(
            job_type=JobType.GFWL,
            user_id=user_id,
            urls=urls,
            total_urls=len(urls),
            team_data=team_data,
        )

        assert job.job_type == JobType.GFWL
        assert job.team_data == team_data
        assert job.urls == urls

    @pytest.mark.unit
    def test_job_status_enum(self) -> None:
        """Test JobStatus enum values."""
        assert JobStatus.PENDING.value == "pending"
        assert JobStatus.RUNNING.value == "running"
        assert JobStatus.COMPLETED.value == "completed"
        assert JobStatus.FAILED.value == "failed"
        assert JobStatus.CANCELLED.value == "cancelled"

    @pytest.mark.unit
    def test_job_type_enum(self) -> None:
        """Test JobType enum values."""
        assert JobType.INDIVIDUAL.value == "individual"
        assert JobType.GFWL.value == "gfwl"

    @pytest.mark.unit
    def test_job_progress_tracking(self) -> None:
        """Test job progress tracking fields."""
        user_id = uuid.uuid4()

        job = Job(
            job_type=JobType.INDIVIDUAL,
            user_id=user_id,
            urls=["url1", "url2", "url3"],
            total_urls=3,
            processed_urls=1,
        )

        assert job.total_urls == 3
        assert job.processed_urls == 1

        # Simulate progress update
        job.processed_urls = 2
        assert job.processed_urls == 2

    @pytest.mark.unit
    def test_job_error_handling(self) -> None:
        """Test job error message field."""
        user_id = uuid.uuid4()

        job = Job(
            job_type=JobType.INDIVIDUAL,
            user_id=user_id,
            urls=["url1"],
            total_urls=1,
            status=JobStatus.FAILED,
            error_message="Network timeout",
        )

        assert job.status == JobStatus.FAILED
        assert job.error_message == "Network timeout"

    @pytest.mark.unit
    def test_job_sharing_features(self) -> None:
        """Test job sharing functionality."""
        user_id = uuid.uuid4()

        job = Job(
            job_type=JobType.INDIVIDUAL,
            user_id=user_id,
            urls=["url1"],
            total_urls=1,
            is_public=True,
        )

        assert job.is_public is True
        assert job.shareable_id is None  # Will be set by database default

    @pytest.mark.unit
    def test_job_timestamps(self) -> None:
        """Test job timestamp fields."""
        user_id = uuid.uuid4()
        start_time = datetime.now()

        job = Job(
            job_type=JobType.INDIVIDUAL,
            user_id=user_id,
            urls=["url1"],
            total_urls=1,
            started_at=start_time,
        )

        assert job.started_at == start_time
        assert job.completed_at is None


class TestScrapedDataModel:
    """Unit tests for ScrapedData model."""

    @pytest.mark.unit
    def test_scraped_data_creation(self) -> None:
        """Test ScrapedData model creation."""
        url = "https://example.com/replay/123"
        s3_key = "scraped-data/2024/01/replay-123.json"

        scraped_data = ScrapedData(url=url, s3_key=s3_key)

        assert scraped_data.url == url
        assert scraped_data.s3_key == s3_key
        assert scraped_data.id is None  # Will be set by database default
        assert scraped_data.created_at is None  # Will be set by database default
        assert scraped_data.updated_at is None  # Will be set by database default

    @pytest.mark.unit
    def test_scraped_data_url_mapping(self) -> None:
        """Test URL to S3 key mapping functionality."""
        test_cases = [
            {
                "url": "https://duelingbook.com/replay?id=123",
                "s3_key": "replays/123/raw_data.json",
            },
            {
                "url": "https://duelingbook.com/replay?id=456",
                "s3_key": "replays/456/raw_data.json",
            },
        ]

        for case in test_cases:
            scraped_data = ScrapedData(url=case["url"], s3_key=case["s3_key"])
            assert scraped_data.url == case["url"]
            assert scraped_data.s3_key == case["s3_key"]


class TestGFWLTeamSubmissionModel:
    """Unit tests for GFWLTeamSubmission model."""

    @pytest.mark.unit
    def test_gfwl_submission_creation(self) -> None:
        """Test GFWLTeamSubmission model creation."""
        job_id = uuid.uuid4()
        team_name = "Test Team"
        discovered_players = ["Player1", "Player2", "Player3"]

        submission = GFWLTeamSubmission(
            job_id=job_id,
            team_name=team_name,
            discovered_players=discovered_players,
        )

        assert submission.job_id == job_id
        assert submission.team_name == team_name
        assert submission.discovered_players == discovered_players
        assert submission.confirmed_players is None
        assert submission.confirmation_status is None  # Will be set by database default

    @pytest.mark.unit
    def test_gfwl_player_confirmation(self) -> None:
        """Test GFWL player confirmation workflow."""
        job_id = uuid.uuid4()
        discovered_players = ["Player1", "Player2", "Player3", "Player4"]
        confirmed_players = ["Player1", "Player3"]

        submission = GFWLTeamSubmission(
            job_id=job_id,
            team_name="Test Team",
            discovered_players=discovered_players,
        )

        # Initially no confirmed players
        assert submission.confirmed_players is None
        assert submission.confirmation_status is None  # Will be set by database default

        # After confirmation
        submission.confirmed_players = confirmed_players
        submission.confirmation_status = "confirmed"

        assert submission.confirmed_players == confirmed_players
        assert submission.confirmation_status == "confirmed"

    @pytest.mark.unit
    def test_gfwl_submission_validation(self) -> None:
        """Test GFWLTeamSubmission field validation."""
        job_id = uuid.uuid4()

        # Test with empty discovered players list
        submission = GFWLTeamSubmission(
            job_id=job_id,
            team_name="Empty Team",
            discovered_players=[],
        )

        assert submission.discovered_players == []
        assert submission.team_name == "Empty Team"

    @pytest.mark.unit
    def test_gfwl_submission_relationships(self) -> None:
        """Test GFWLTeamSubmission model relationships."""
        job_id = uuid.uuid4()

        submission = GFWLTeamSubmission(
            job_id=job_id,
            team_name="Test Team",
            discovered_players=["Player1"],
        )

        # Test that job relationship exists
        assert hasattr(submission, "job")
        assert submission.job_id == job_id


class TestModelRelationships:
    """Integration tests for model relationships."""

    @pytest.mark.unit
    def test_user_job_relationship(self) -> None:
        """Test User-Job relationship."""
        user = User(clerk_user_id="clerk_12345")
        user_id = uuid.uuid4()

        job1 = Job(
            job_type=JobType.INDIVIDUAL,
            user_id=user_id,
            urls=["url1"],
            total_urls=1,
        )

        job2 = Job(
            job_type=JobType.GFWL,
            user_id=user_id,
            urls=["url2"],
            total_urls=1,
        )

        # Test that relationship attributes exist
        assert hasattr(user, "jobs")
        assert hasattr(job1, "user")
        assert hasattr(job2, "user")

    @pytest.mark.unit
    def test_job_gfwl_submission_relationship(self) -> None:
        """Test Job-GFWLTeamSubmission relationship."""
        job_id = uuid.uuid4()

        job = Job(
            job_type=JobType.GFWL,
            user_id=uuid.uuid4(),
            urls=["url1"],
            total_urls=1,
        )

        submission = GFWLTeamSubmission(
            job_id=job_id,
            team_name="Test Team",
            discovered_players=["Player1"],
        )

        # Test that relationship attributes exist
        assert hasattr(job, "gfwl_submissions")
        assert hasattr(submission, "job")
        assert submission.job_id == job_id


class TestModelValidation:
    """Tests for model field validation and constraints."""

    @pytest.mark.unit
    def test_required_fields_validation(self) -> None:
        """Test that required fields are properly defined."""
        # User required fields
        user_fields = User.__table__.columns.keys()
        assert "clerk_user_id" in user_fields

        # Job required fields
        job_fields = Job.__table__.columns.keys()
        required_job_fields = [
            "job_type",
            "user_id",
            "urls",
            "total_urls",
            "shareable_id",
        ]
        for field in required_job_fields:
            assert field in job_fields

        # ScrapedData required fields
        scraped_fields = ScrapedData.__table__.columns.keys()
        assert "url" in scraped_fields
        assert "s3_key" in scraped_fields

        # GFWLTeamSubmission required fields
        gfwl_fields = GFWLTeamSubmission.__table__.columns.keys()
        required_gfwl_fields = ["job_id", "team_name", "discovered_players"]
        for field in required_gfwl_fields:
            assert field in gfwl_fields

    @pytest.mark.unit
    def test_enum_constraints(self) -> None:
        """Test enum field constraints."""
        # Test all JobStatus values
        valid_statuses = [
            JobStatus.PENDING,
            JobStatus.RUNNING,
            JobStatus.COMPLETED,
            JobStatus.FAILED,
            JobStatus.CANCELLED,
        ]

        for status in valid_statuses:
            assert isinstance(status, JobStatus)
            assert isinstance(status.value, str)

        # Test all JobType values
        valid_types = [JobType.INDIVIDUAL, JobType.GFWL]

        for job_type in valid_types:
            assert isinstance(job_type, JobType)
            assert isinstance(job_type.value, str)
