from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.worker import Worker


def search_workers(
    db: Session,
    q: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> tuple[list[Worker], int]:
    stmt = select(Worker)

    if active_only:
        stmt = stmt.where(Worker.is_active.is_(True))

    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Worker.employee_id.ilike(like),
                Worker.full_name.ilike(like),
                Worker.job_title.ilike(like),
                Worker.department_id.ilike(like),
                Worker.section_id.ilike(like),
                Worker.administration_id.ilike(like),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Worker.full_name).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_worker(db: Session, employee_id: str) -> Worker | None:
    stmt = select(Worker).where(Worker.employee_id == employee_id)
    return db.execute(stmt).scalars().first()
