from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.worker import Worker
from app.repositories import worker_repository


def list_workers(db: Session, limit: int, offset: int) -> tuple[list[Worker], int]:
    return worker_repository.list_workers(db, limit, offset)


def get_worker(db: Session, employee_id: str) -> Worker:
    worker = worker_repository.get_worker(db, employee_id)
    if worker is None:
        raise ApiError(
            status_code=404,
            error="WORKER_NOT_FOUND",
            message="The requested worker was not found",
        )
    return worker
