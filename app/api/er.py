from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.core.security import require_er_api_key
from app.schemas.er_visit import ErVisit, ErVisitListResponse
from app.services import er_visit_service

# Mounted under the ER API prefix (/his-er/api/er/v1), not the Directory API:
# 3iSoft serves it from a separate application with its own key.
router = APIRouter(
    tags=["ER"],
    dependencies=[Depends(require_er_api_key)],
)


@router.get("/current-visits", response_model=ErVisitListResponse)
def list_current_visits(db: DbSession) -> ErVisitListResponse:
    items = er_visit_service.list_current_visits(db)
    return ErVisitListResponse(
        items=[ErVisit.model_validate(item) for item in items],
        total=len(items),
    )
