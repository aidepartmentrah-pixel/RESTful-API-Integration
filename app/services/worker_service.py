from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.worker import Worker
from app.repositories import worker_repository


def search_workers(
    db: Session, q: str | None, active_only: bool, limit: int, offset: int
) -> tuple[list[Worker], int]:
    return worker_repository.search_workers(db, q, active_only, limit, offset)


def get_worker(db: Session, employee_id: str) -> Worker:
    worker = worker_repository.get_worker(db, employee_id)
    if worker is None:
        raise ApiError(
            status_code=404,
            error="WORKER_NOT_FOUND",
            message="The requested worker was not found",
        )
    return worker
