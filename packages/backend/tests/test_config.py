import pytest
from unittest.mock import patch
import os

from app.config import Settings


class TestSettings:
    """Unit tests for Settings configuration."""

    @pytest.mark.unit
    def test_settings_default_values(self) -> None:
        """Test that Settings has correct default values."""
        with patch.dict(
            os.environ,
            {
                "APP_TITLE": "Test App",
                "API_PREFIX": "/api/v1",
                "POSTGRES_USER": "test_user",
                "POSTGRES_PASSWORD": "test_pass",
                "POSTGRES_DB": "test_db",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
            },
            clear=True,
        ):
            settings = Settings()

            assert settings.APP_TITLE == "Test App"
            assert settings.API_PREFIX == "/api/v1"
            assert settings.ENVIRONMENT == "local"  # default value
            # Test that default CORS origins are applied when not explicitly set
            assert settings.BACKEND_CORS_ORIGINS == ["*"]  # default value from Field
            assert settings.POSTGRES_USER == "test_user"
            assert settings.POSTGRES_PASSWORD == "test_pass"
            assert settings.POSTGRES_DB == "test_db"
            assert settings.POSTGRES_HOST == "localhost"
            assert settings.POSTGRES_PORT == 5432

    @pytest.mark.unit
    def test_database_url_construction(self) -> None:
        """Test that DATABASE_URL is constructed correctly."""
        with patch.dict(
            os.environ,
            {
                "APP_TITLE": "Test App",
                "API_PREFIX": "/api/v1",
                "POSTGRES_USER": "myuser",
                "POSTGRES_PASSWORD": "mypass",
                "POSTGRES_DB": "mydb",
                "POSTGRES_HOST": "db.example.com",
                "POSTGRES_PORT": "5433",
            },
            clear=True,
        ):
            settings = Settings()
            expected_url = "postgresql+asyncpg://myuser:mypass@db.example.com:5433/mydb"
            assert settings.DATABASE_URL == expected_url

    @pytest.mark.unit
    def test_environment_validation(self) -> None:
        """Test that ENVIRONMENT accepts only valid values."""
        valid_environments = ["local", "staging", "production"]

        for env in valid_environments:
            with patch.dict(
                os.environ,
                {
                    "APP_TITLE": "Test App",
                    "API_PREFIX": "/api/v1",
                    "ENVIRONMENT": env,
                    "POSTGRES_USER": "test",
                    "POSTGRES_PASSWORD": "test",
                    "POSTGRES_DB": "test",
                    "POSTGRES_HOST": "localhost",
                    "POSTGRES_PORT": "5432",
                },
                clear=True,
            ):
                settings = Settings()
                assert settings.ENVIRONMENT == env

    @pytest.mark.unit
    def test_cors_origins_list(self) -> None:
        """Test that BACKEND_CORS_ORIGINS handles list values correctly."""
        with patch.dict(
            os.environ,
            {
                "APP_TITLE": "Test App",
                "API_PREFIX": "/api/v1",
                "BACKEND_CORS_ORIGINS": '["http://localhost:3000", "https://app.example.com"]',
                "POSTGRES_USER": "test",
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB": "test",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
            },
            clear=True,
        ):
            settings = Settings()
            expected_origins = ["http://localhost:3000", "https://app.example.com"]
            assert settings.BACKEND_CORS_ORIGINS == expected_origins

    @pytest.mark.unit
    def test_all_required_fields_are_present(self) -> None:
        """Test that all required fields are defined in the Settings class."""
        # This test ensures that we haven't accidentally made required fields optional
        required_fields = {
            "APP_TITLE",
            "API_PREFIX",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "POSTGRES_HOST",
            "POSTGRES_PORT",
            "CLERK_JWT_ISSUER",
        }

        # Get all field names from the Settings model
        settings_fields = set(Settings.model_fields.keys())

        # Check that all required fields are present
        for field in required_fields:
            assert field in settings_fields, (
                f"Required field {field} is missing from Settings"
            )

        # Verify that some fields don't have defaults (are truly required)
        from pydantic_core import PydanticUndefined

        assert Settings.model_fields["APP_TITLE"].default is PydanticUndefined, (
            "APP_TITLE should be required"
        )
        assert Settings.model_fields["POSTGRES_USER"].default is PydanticUndefined, (
            "POSTGRES_USER should be required"
        )

    @pytest.mark.unit
    def test_port_type_conversion(self) -> None:
        """Test that POSTGRES_PORT is correctly converted to int."""
        with patch.dict(
            os.environ,
            {
                "APP_TITLE": "Test App",
                "API_PREFIX": "/api/v1",
                "POSTGRES_USER": "test",
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB": "test",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "9999",  # string value
            },
            clear=True,
        ):
            settings = Settings()
            assert isinstance(settings.POSTGRES_PORT, int)
            assert settings.POSTGRES_PORT == 9999

    @pytest.mark.unit
    def test_clerk_jwks_url_property(self) -> None:
        """Test that CLERK_JWKS_URL is constructed correctly from CLERK_JWT_ISSUER."""
        with patch.dict(
            os.environ,
            {
                "APP_TITLE": "Test App",
                "API_PREFIX": "/api/v1",
                "POSTGRES_USER": "test",
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB": "test",
                "POSTGRES_HOST": "localhost",
                "POSTGRES_PORT": "5432",
                "CLERK_JWT_ISSUER": "https://test-app.clerk.accounts.dev",
            },
            clear=True,
        ):
            settings = Settings()
            expected_jwks_url = (
                "https://test-app.clerk.accounts.dev/.well-known/jwks.json"
            )
            assert settings.CLERK_JWKS_URL == expected_jwks_url

    @pytest.mark.unit
    def test_clerk_jwks_url_empty_issuer(self) -> None:
        """Test CLERK_JWKS_URL behavior with empty issuer."""
        # Create settings directly with empty issuer to avoid env var interference
        settings = Settings(
            APP_TITLE="Test App",
            API_PREFIX="/api/v1",
            POSTGRES_USER="test",
            POSTGRES_PASSWORD="test",
            POSTGRES_DB="test",
            POSTGRES_HOST="localhost",
            POSTGRES_PORT=5432,
            CLERK_JWT_ISSUER="",
        )
        expected_jwks_url = "/.well-known/jwks.json"
        assert settings.CLERK_JWKS_URL == expected_jwks_url
