from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, LimitParam, OffsetParam
from app.core.security import require_api_key
from app.schemas.worker import HrWorker, HrWorkerListResponse
from app.services import hr_worker_service

router = APIRouter(
    prefix="/hr-workers",
    tags=["HR Workers"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=HrWorkerListResponse)
def list_hr_workers(
    db: DbSession,
    administration: Annotated[str | None, Query()] = None,
    section: Annotated[str | None, Query()] = None,
    department: Annotated[str | None, Query()] = None,
    limit: LimitParam = 10,
    offset: OffsetParam = 0,
) -> HrWorkerListResponse:
    items, total = hr_worker_service.list_hr_workers(db, administration, section, department, limit, offset)
    return HrWorkerListResponse(
        items=[HrWorker(**item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{employee_id}", response_model=HrWorker)
def get_hr_worker(db: DbSession, employee_id: str) -> HrWorker:
    return HrWorker(**hr_worker_service.get_hr_worker(db, employee_id))
