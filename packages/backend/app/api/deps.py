from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.database import get_db_session
from app.db.models import User

UserDep = Annotated[User, Depends(get_current_user)]
DBDep = Annotated[AsyncSession, Depends(get_db_session)]
