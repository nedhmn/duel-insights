from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from app.db.models import JobType


class PublicJobResultsResponse(BaseModel):
    shareable_id: UUID
    job_type: JobType
    summary: dict[str, Any]
    detailed_results: dict[str, Any]
    generated_at: datetime

    class Config:
        arbitrary_types_allowed = True
