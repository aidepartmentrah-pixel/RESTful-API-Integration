from fastapi import APIRouter, Depends

from app.api.deps import DbSession, LimitParam, OffsetParam
from app.core.security import require_api_key
from app.schemas.worker import Worker, WorkerListResponse
from app.services import worker_service

router = APIRouter(
    prefix="/workers",
    tags=["Workers"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=WorkerListResponse)
def list_workers(
    db: DbSession,
    limit: LimitParam = 10,
    offset: OffsetParam = 0,
) -> WorkerListResponse:
    items, total = worker_service.list_workers(db, limit, offset)
    return WorkerListResponse(
        items=[Worker.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{employee_id}", response_model=Worker)
def get_worker(db: DbSession, employee_id: str) -> Worker:
    worker = worker_service.get_worker(db, employee_id)
    # OpenAPI v1.1 quirk: HR's single-employee lookup exposes no active flag,
    # so is_active is always reported true via this route specifically.
    return Worker.model_validate(worker).model_copy(update={"is_active": True})
