from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings

db_engine = create_async_engine(
    settings.DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20
)

db_session = async_sessionmaker(
    bind=db_engine, expire_on_commit=False, class_=AsyncSession
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session = db_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
