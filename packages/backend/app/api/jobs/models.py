from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models import JobStatus, JobType


class JobResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    job_type: JobType
    total_urls: int
    processed_urls: int = 0
    error_message: str | None = None
    shareable_id: UUID | None = None
    is_public: bool = False
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class JobResultsResponse(BaseModel):
    job_id: UUID
    job_type: JobType
    status: JobStatus
    summary: dict[str, Any]
    detailed_results: dict[str, Any]
    generated_at: datetime

    class Config:
        arbitrary_types_allowed = True


class JobShareRequest(BaseModel):
    is_public: bool


class JobShareResponse(BaseModel):
    job_id: UUID
    shareable_id: UUID
    is_public: bool
    share_url: str


class JobProgressResponse(BaseModel):
    job_id: UUID
    status: JobStatus
    processed: int
    total: int
    progress_percentage: float = Field(..., ge=0, le=100)
    error_message: str | None = None


class JobListResponse(BaseModel):
    jobs: list[dict[str, Any]]
    total: int
    page: int
    per_page: int
    total_pages: int
