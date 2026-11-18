import hmac

from fastapi import Header

from app.core.config import get_settings
from app.core.errors import ApiError

API_KEY_HEADER = "X-API-Key"


def _check(x_api_key: str | None, expected: str) -> None:
    # OpenAPI v1.1: comparison must be length-constant.
    if not x_api_key or not hmac.compare_digest(x_api_key, expected):
        raise ApiError(
            status_code=401,
            error="UNAUTHORIZED",
            message="Missing or invalid API key",
        )


async def require_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER)) -> None:
    _check(x_api_key, get_settings().api_key)


async def require_er_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER)) -> None:
    """ER API (3iSoft v1.2): its own key, separate from the Directory API key."""
    _check(x_api_key, get_settings().er_api_key)
