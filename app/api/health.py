from datetime import datetime, timezone

from fastapi import APIRouter, Response

from app.api.deps import DbSession
from app.schemas.common import HealthResponse
from app.services import health_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health(db: DbSession, response: Response) -> HealthResponse:
    timestamp = datetime.now(timezone.utc)
    healthy = health_service.check_database(db)
    if not healthy:
        response.status_code = 503

    return HealthResponse(
        status="healthy" if healthy else "unhealthy",
        service="his-general-directory",
        api_version="1.0.0",
        timestamp=timestamp,
    )
