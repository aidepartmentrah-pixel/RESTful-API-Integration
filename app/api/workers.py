from typing import Annotated

from fastapi import APIRouter, Depends, Query

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
def search_workers(
    db: DbSession,
    q: Annotated[str | None, Query(min_length=1)] = None,
    active_only: Annotated[bool, Query()] = True,
    limit: LimitParam = 100,
    offset: OffsetParam = 0,
) -> WorkerListResponse:
    items, total = worker_service.search_workers(db, q, active_only, limit, offset)
    return WorkerListResponse(
        items=[Worker.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{employee_id}", response_model=Worker)
def get_worker(db: DbSession, employee_id: str) -> Worker:
    worker = worker_service.get_worker(db, employee_id)
    return Worker.model_validate(worker)
