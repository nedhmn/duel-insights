import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from typing import AsyncGenerator
from sqlalchemy.pool import StaticPool

import sys
from pathlib import Path

# Add the parent directory to sys.path for importlib mode
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Settings
from app.db.database import get_db_session
from app.db.models import Base
from app.main import app


# Note: With pytest-asyncio in auto mode, we don't need a custom event_loop fixture
# The default event loop management is handled automatically


@pytest.fixture
def test_settings() -> Settings:
    """Test settings with in-memory database."""
    return Settings(
        APP_TITLE="Test Duel Insights API",
        API_PREFIX="/api/v1",
        ENVIRONMENT="local",
        POSTGRES_USER="test",
        POSTGRES_PASSWORD="test",
        POSTGRES_DB="test_db",
        POSTGRES_HOST="localhost",
        POSTGRES_PORT=5432,
    )


@pytest.fixture
async def test_db_session(
    test_settings: Settings,
) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session with in-memory SQLite."""
    # Use in-memory SQLite for tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def test_client(
    test_db_session: AsyncSession, test_settings: Settings
) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with dependency overrides."""

    def override_get_db() -> AsyncSession:
        return test_db_session

    def override_settings() -> Settings:
        return test_settings

    app.dependency_overrides[get_db_session] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()
