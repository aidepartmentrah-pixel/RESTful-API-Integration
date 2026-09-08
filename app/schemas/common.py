from datetime import datetime

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str


class HealthResponse(BaseModel):
    status: str
    service: str | None = None
    api_version: str | None = None
    timestamp: datetime | None = None
