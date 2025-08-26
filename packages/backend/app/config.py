from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_TITLE: str
    API_PREFIX: str
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(default="local")
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["*"])

    # Database
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # Clerk Authentication
    CLERK_JWT_ISSUER: str = Field(default="")
    CLERK_JWT_AUDIENCE: str = Field(default="")
    CLERK_SECRET_KEY: str = Field(default="")

    # AWS S3
    AWS_ACCESS_KEY_ID: str = Field(default="")
    AWS_SECRET_ACCESS_KEY: str = Field(default="")
    AWS_S3_BUCKET: str = Field(default="")
    AWS_S3_REGION: str = Field(default="us-east-1")

    # Redis (Celery broker/backend + caching)
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # BrightData
    BRIGHTDATA_USERNAME: str = Field(default="")
    BRIGHTDATA_PASSWORD: str = Field(default="")
    BRIGHTDATA_ENDPOINT: str = Field(default="")

    # Job Configuration
    MAX_URLS_PER_JOB: int = Field(default=100)
    JOB_TIMEOUT_MINUTES: int = Field(default=60)
    RESULTS_RETENTION_DAYS: int = Field(default=30)

    @property
    def DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def CELERY_BROKER_URL(self) -> str:
        return self.REDIS_URL

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return self.REDIS_URL


settings = Settings(
    APP_TITLE="Duel Insights API",
    API_PREFIX="/api/v1",
    BACKEND_CORS_ORIGINS=["http://localhost:3000"],
)
