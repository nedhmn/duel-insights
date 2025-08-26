import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    TIMESTAMP,
    String,
    Integer,
    Boolean,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, nullable=False, default=uuid.uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    INDIVIDUAL = "individual"
    GFWL = "gfwl"


class User(BaseModel):
    __tablename__ = "users"

    clerk_user_id: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    # Relationships
    jobs: Mapped[list["Job"]] = relationship("Job", back_populates="user")


class Job(BaseModel):
    __tablename__ = "jobs"

    job_type: Mapped[JobType] = mapped_column(nullable=False)
    status: Mapped[JobStatus] = mapped_column(default=JobStatus.PENDING, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )

    # Input data
    urls: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    team_data: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )  # For GFWL mode

    # Progress tracking
    total_urls: Mapped[int] = mapped_column(Integer, nullable=False)
    processed_urls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    # Shareable results
    shareable_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        unique=True,
        index=True,
        nullable=False,
        default=uuid.uuid4,
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Timestamps
    started_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="jobs")
    gfwl_submissions: Mapped[list["GFWLTeamSubmission"]] = relationship(
        "GFWLTeamSubmission", back_populates="job"
    )

    __table_args__ = (
        Index("ix_jobs_user_id_status", "user_id", "status"),
        Index("ix_jobs_status_created_at", "status", "created_at"),
        Index("ix_jobs_user_id_job_type", "user_id", "job_type"),
    )


class ScrapedData(BaseModel):
    __tablename__ = "scraped_data"

    url: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    s3_key: Mapped[str] = mapped_column(
        String, nullable=False
    )  # S3 object key for raw scraped JSON


class GFWLTeamSubmission(BaseModel):
    __tablename__ = "gfwl_team_submissions"

    job_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("jobs.id"), nullable=False, index=True
    )
    team_name: Mapped[str] = mapped_column(String(255), nullable=False)
    discovered_players: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    confirmed_players: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    confirmation_status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, confirmed

    # Relationships
    job: Mapped["Job"] = relationship("Job", back_populates="gfwl_submissions")

    __table_args__ = (
        Index(
            "ix_gfwl_team_submissions_job_id_status", "job_id", "confirmation_status"
        ),
    )
