from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class TestIndividualRoutes:
    @pytest.fixture
    async def mock_current_user(self, test_db_session: AsyncSession) -> User:
        user = User(clerk_user_id="test_user_123")
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        return user

    @pytest.fixture
    def auth_headers(self) -> dict[str, str]:
        return {"Authorization": "Bearer valid_jwt_token"}

    async def test_submit_individual_job_success(
        self,
        test_client: AsyncClient,
        auth_headers: dict[str, str],
        mock_current_user: User,
    ) -> None:
        with patch(
            "app.auth.dependencies.get_current_user", return_value=mock_current_user
        ):
            request_data = {
                "urls": ["https://example.com/game1", "https://example.com/game2"]
            }

            response = await test_client.post(
                "/api/v1/jobs/individual/",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["job_type"] == "individual"
            assert data["status"] == "pending"
            assert data["total_urls"] == 2

    async def test_submit_individual_job_invalid_urls(
        self,
        test_client: AsyncClient,
        auth_headers: dict[str, str],
        mock_current_user: User,
    ) -> None:
        with patch(
            "app.auth.dependencies.get_current_user", return_value=mock_current_user
        ):
            request_data = {"urls": ["not_a_valid_url"]}

            response = await test_client.post(
                "/api/v1/jobs/individual/",
                json=request_data,
                headers=auth_headers,
            )

            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_submit_individual_job_no_auth(
        self, test_client: AsyncClient
    ) -> None:
        request_data = {"urls": ["https://example.com/game1"]}

        response = await test_client.post("/api/v1/jobs/individual/", json=request_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
