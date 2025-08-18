from typing import Literal

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    status: Literal["ok"] = Field(default="ok")
