import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from jose import jwt

from app.auth.jwt_handler import JWTHandler, jwt_handler
from app.auth.models import UserContext, AuthError
from app.auth.dependencies import get_user_context, get_current_user
from app.db.models import User


# Global fixtures for auth tests
@pytest.fixture
def mock_jwks():
    """Mock JWKS response."""
    return {
        "keys": [
            {
                "kid": "test-key-id",
                "kty": "RSA",
                "use": "sig",
                "n": "test-n-value",
                "e": "AQAB",
                "alg": "RS256",
            }
        ]
    }


@pytest.fixture
def valid_jwt_claims():
    """Valid JWT claims for testing."""
    return {
        "sub": "user_2abc123def456",
        "iss": "https://test-app.clerk.accounts.dev",
        "aud": "test-audience",
        "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
        "iat": int(datetime.now(timezone.utc).timestamp()),
        "email": "test@example.com",
        "email_verified": True,
        "given_name": "John",
        "family_name": "Doe",
        "name": "John Doe",
        "picture": "https://example.com/avatar.jpg",
    }


class TestJWTHandler:
    """Unit tests for JWT token handling."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_jwks_success(self, mock_jwks):
        """Test successful JWKS retrieval."""
        handler = JWTHandler()

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_jwks
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await handler.get_jwks()

            assert result == mock_jwks
            assert handler._jwks_cache == mock_jwks
            assert handler._jwks_cache_expires is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_jwks_http_error(self):
        """Test JWKS retrieval with HTTP error."""
        handler = JWTHandler()

        with patch("httpx.AsyncClient") as mock_client:
            import httpx

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPError("Network error")
            )

            with pytest.raises(ValueError, match="Failed to fetch JWKS"):
                await handler.get_jwks()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_jwks_caching(self, mock_jwks):
        """Test JWKS caching behavior."""
        handler = JWTHandler()

        # Mock successful first call
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.json.return_value = mock_jwks
            mock_response.raise_for_status.return_value = None

            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            # First call should fetch from network
            result1 = await handler.get_jwks()
            assert result1 == mock_jwks

            # Second call should use cache (no network call)
            result2 = await handler.get_jwks()
            assert result2 == mock_jwks

            # Verify only one network call was made
            mock_client.return_value.__aenter__.return_value.get.assert_called_once()

    @pytest.mark.unit
    def test_extract_user_info(self, valid_jwt_claims):
        """Test user info extraction from JWT claims."""
        handler = JWTHandler()

        user_info = handler.extract_user_info(valid_jwt_claims)

        assert user_info["clerk_user_id"] == "user_2abc123def456"
        assert user_info["email_verified"] is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_success(self, mock_jwks, valid_jwt_claims):
        """Test successful token verification."""
        handler = JWTHandler()
        test_token = "test.jwt.token"

        with patch.object(handler, "get_jwks", return_value=mock_jwks):
            with patch(
                "jose.jwt.get_unverified_header", return_value={"kid": "test-key-id"}
            ):
                with patch("jose.jwt.decode", return_value=valid_jwt_claims):
                    result = await handler.verify_token(test_token)

                    assert result == valid_jwt_claims

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_empty(self):
        """Test token verification with empty token."""
        handler = JWTHandler()

        with pytest.raises(ValueError, match="Token is required"):
            await handler.verify_token("")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_missing_kid(self, mock_jwks):
        """Test token verification with missing key ID."""
        handler = JWTHandler()
        test_token = "test.jwt.token"

        with patch.object(handler, "get_jwks", return_value=mock_jwks):
            with patch("jose.jwt.get_unverified_header", return_value={}):
                with pytest.raises(ValueError, match="Token missing key ID"):
                    await handler.verify_token(test_token)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_token_key_not_found(self, mock_jwks):
        """Test token verification with key not found in JWKS."""
        handler = JWTHandler()
        test_token = "test.jwt.token"

        with patch.object(handler, "get_jwks", return_value=mock_jwks):
            with patch(
                "jose.jwt.get_unverified_header", return_value={"kid": "wrong-key-id"}
            ):
                with pytest.raises(
                    ValueError, match="Key with ID wrong-key-id not found"
                ):
                    await handler.verify_token(test_token)


class TestUserContext:
    """Unit tests for UserContext model."""

    @pytest.mark.unit
    def test_user_context_creation(self):
        """Test UserContext model creation."""
        context = UserContext(
            clerk_user_id="user_123",
            email_verified=True,
        )

        assert context.clerk_user_id == "user_123"
        assert context.email_verified is True
        assert context.user_id is None  # Not set initially

    @pytest.mark.unit
    def test_user_context_minimal(self):
        """Test UserContext with minimal required data."""
        context = UserContext(clerk_user_id="user_123")

        assert context.clerk_user_id == "user_123"
        assert context.email_verified is False


class TestAuthError:
    """Unit tests for AuthError exception."""

    @pytest.mark.unit
    def test_auth_error_default(self):
        """Test AuthError with default status code."""
        error = AuthError("Test error")

        assert error.message == "Test error"
        assert error.status_code == 401
        assert str(error) == "Test error"

    @pytest.mark.unit
    def test_auth_error_custom_status(self):
        """Test AuthError with custom status code."""
        error = AuthError("Forbidden", 403)

        assert error.message == "Forbidden"
        assert error.status_code == 403


class TestAuthDependencies:
    """Integration tests for authentication dependencies."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_context_success(self, valid_jwt_claims):
        """Test successful user context extraction."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="valid.jwt.token"
        )

        with patch.object(jwt_handler, "verify_token", return_value=valid_jwt_claims):
            with patch.object(jwt_handler, "extract_user_info") as mock_extract:
                mock_extract.return_value = {
                    "clerk_user_id": "user_123",
                    "email_verified": True,
                }

                result = await get_user_context(credentials)

                assert isinstance(result, UserContext)
                assert result.clerk_user_id == "user_123"
                assert result.email_verified is True

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_context_no_credentials(self):
        """Test user context extraction without credentials."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await get_user_context(None)

        assert exc_info.value.status_code == 401
        assert "Authorization header required" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_user_context_invalid_token(self):
        """Test user context extraction with invalid token."""
        from fastapi import HTTPException
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid.jwt.token"
        )

        with patch.object(
            jwt_handler, "verify_token", side_effect=ValueError("Invalid token")
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_user_context(credentials)

            assert exc_info.value.status_code == 401
            assert "Invalid token" in exc_info.value.detail

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_existing(self, test_db_session):
        """Test getting existing user from database."""
        import uuid
        from datetime import datetime

        # Create a test user manually with required fields
        user_id = uuid.uuid4()
        now = datetime.now()

        existing_user = User(
            id=user_id, clerk_user_id="user_123", created_at=now, updated_at=now
        )
        test_db_session.add(existing_user)
        await test_db_session.commit()
        await test_db_session.refresh(existing_user)

        # Create user context
        user_context = UserContext(clerk_user_id="user_123")

        # Get current user
        result = await get_current_user(user_context, test_db_session)

        assert result.clerk_user_id == "user_123"
        assert result.id == existing_user.id
        assert user_context.user_id == str(existing_user.id)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_user_new(self, test_db_session):
        """Test creating new user when doesn't exist."""
        # Create user context for non-existent user
        user_context = UserContext(clerk_user_id="new_user_456")

        # Mock the database operations to avoid server defaults
        with patch.object(test_db_session, "add") as mock_add:
            with patch.object(test_db_session, "commit") as mock_commit:
                with patch.object(test_db_session, "refresh") as mock_refresh:
                    import uuid
                    from datetime import datetime

                    # Create a mock user that would be returned
                    mock_user = User(
                        id=uuid.uuid4(),
                        clerk_user_id="new_user_456",
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                    )

                    # Mock refresh to populate the user
                    def mock_refresh_side_effect(user):
                        user.id = mock_user.id
                        user.created_at = mock_user.created_at
                        user.updated_at = mock_user.updated_at

                    mock_refresh.side_effect = mock_refresh_side_effect

                    # Get current user (should create new one)
                    result = await get_current_user(user_context, test_db_session)

                    assert result.clerk_user_id == "new_user_456"
                    assert result.id is not None
                    assert user_context.user_id == str(result.id)

                    # Verify mocks were called
                    mock_add.assert_called_once()
                    mock_commit.assert_called_once()
                    mock_refresh.assert_called_once()
