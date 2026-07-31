from fastapi import APIRouter, Response

from app.api.deps import DbSession
from app.schemas.common import HealthResponse
from app.services import health_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health(db: DbSession, response: Response) -> HealthResponse:
    if health_service.check_database(db):
        return HealthResponse(status="healthy")

    response.status_code = 503
    return HealthResponse(status="unhealthy")
