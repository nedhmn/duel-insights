from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.jobs.results.models import PublicJobResultsResponse
from app.api.jobs.results.services import get_public_results
from app.db.database import get_db_session

router = APIRouter()

DBDep = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/{shareable_id}", response_model=PublicJobResultsResponse)
async def get_shared_results(
    shareable_id: UUID,
    db: DBDep,
) -> PublicJobResultsResponse:
    return await get_public_results(db, shareable_id)
