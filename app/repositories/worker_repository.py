from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.worker import Worker


def list_workers(
    db: Session,
    limit: int,
    offset: int,
) -> tuple[list[Worker], int]:
    # OpenAPI v1.1 drops `q`/`active_only` from /workers entirely -- the real
    # server was found to silently ignore `q`, so the contract no longer
    # offers it. This always lists active workers only.
    stmt = select(Worker).where(Worker.is_active.is_(True))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Worker.full_name).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_worker(db: Session, employee_id: str) -> Worker | None:
    stmt = select(Worker).where(Worker.employee_id == employee_id)
    return db.execute(stmt).scalars().first()
