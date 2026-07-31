from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor


def search_doctors(
    db: Session,
    q: str | None,
    active_only: bool,
    limit: int,
    offset: int,
) -> tuple[list[Doctor], int]:
    stmt = select(Doctor)

    if active_only:
        stmt = stmt.where(Doctor.is_active.is_(True))

    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Doctor.doctor_id.ilike(like),
                Doctor.full_name.ilike(like),
                Doctor.specialty_name.ilike(like),
                Doctor.department_name.ilike(like),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Doctor.full_name).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_doctor(db: Session, doctor_id: str) -> Doctor | None:
    stmt = select(Doctor).where(Doctor.doctor_id == doctor_id)
    return db.execute(stmt).scalars().first()
