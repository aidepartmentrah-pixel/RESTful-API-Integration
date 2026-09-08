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
        # OpenAPI v1.1: q matches full name, first name, father name, last
        # name, assistant number, or the numeric id rendered as text (OR).
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Doctor.full_name.ilike(like),
                Doctor.first_name.ilike(like),
                Doctor.father_name.ilike(like),
                Doctor.last_name.ilike(like),
                Doctor.assistant_number.ilike(like),
                Doctor.doctor_id.ilike(like),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Doctor.full_name).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_doctor(db: Session, doctor_id: str) -> Doctor | None:
    stmt = select(Doctor).where(Doctor.doctor_id == doctor_id)
    return db.execute(stmt).scalars().first()
