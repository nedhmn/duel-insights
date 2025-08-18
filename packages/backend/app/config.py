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

    @property
    def DATABASE_URL(self) -> str:
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings(
    APP_TITLE="Duel Insights API",
    API_PREFIX="/api/v1",
    BACKEND_CORS_ORIGINS=["http://localhost:3000"],
)
