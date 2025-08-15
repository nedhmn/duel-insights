from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )

    APP_TITLE: str = Field(default="Duel Insights API")
    API_PREFIX: str = Field(default="/api/v1")
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(default="local")
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])


settings = Settings()
