from fastapi import Header

from app.core.config import get_settings
from app.core.errors import ApiError

API_KEY_HEADER = "X-API-Key"


async def require_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER)) -> None:
    settings = get_settings()
    if not x_api_key or x_api_key != settings.api_key:
        raise ApiError(
            status_code=401,
            error="UNAUTHORIZED",
            message="Missing or invalid API key",
        )
