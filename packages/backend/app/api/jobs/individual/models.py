from pydantic import BaseModel, Field, HttpUrl, field_validator


class JobSubmissionRequest(BaseModel):
    urls: list[HttpUrl] = Field(..., min_length=1, max_length=12)

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v: list[HttpUrl]) -> list[HttpUrl]:
        if not v:
            raise ValueError("At least one URL is required")
        if len(v) > 12:
            raise ValueError("Maximum 12 URLs allowed per individual job")
        return v
