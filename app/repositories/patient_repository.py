from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.patient import Patient


def search_patients(
    db: Session,
    patient_id: str | None,
    first_name: str | None,
    father_name: str | None,
    last_name: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Patient], int]:
    stmt = select(Patient)

    if patient_id:
        stmt = stmt.where(Patient.patient_id == patient_id)

    if first_name:
        like = f"%{first_name}%"
        stmt = stmt.where(or_(Patient.first_name_ar.ilike(like), Patient.first_name_en.ilike(like)))
    if father_name:
        like = f"%{father_name}%"
        stmt = stmt.where(or_(Patient.father_name_ar.ilike(like), Patient.father_name_en.ilike(like)))
    if last_name:
        like = f"%{last_name}%"
        stmt = stmt.where(or_(Patient.last_name_ar.ilike(like), Patient.last_name_en.ilike(like)))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Patient.first_name_ar, Patient.last_name_ar).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_patient(db: Session, patient_id: str) -> Patient | None:
    stmt = select(Patient).where(Patient.patient_id == patient_id)
    return db.execute(stmt).scalars().first()


def get_father_name_candidates(
    db: Session,
    first_name: str,
    last_name: str,
    limit: int,
) -> tuple[list[tuple[str, int]], int]:
    """Distinct, non-blank father-name values (English if stored else Arabic,
    same fallback rule as Patient.first_name/last_name) among patients
    matching first_name+last_name, with a count each.

    Ordered by count descending, ties by father name, so the list is stable
    between calls. Returns (candidates, total) where total is the number of
    distinct candidates *before* `limit` is applied."""
    father_name_display = func.coalesce(Patient.father_name_en, Patient.father_name_ar)
    like_first = f"%{first_name.strip()}%"
    like_last = f"%{last_name.strip()}%"

    grouped = (
        select(father_name_display.label("father_name"), func.count().label("patient_count"))
        .where(
            or_(Patient.first_name_ar.ilike(like_first), Patient.first_name_en.ilike(like_first)),
            or_(Patient.last_name_ar.ilike(like_last), Patient.last_name_en.ilike(like_last)),
            father_name_display.is_not(None),
            func.trim(father_name_display) != "",
        )
        .group_by(father_name_display)
    )

    total = db.scalar(select(func.count()).select_from(grouped.subquery())) or 0
    rows = db.execute(
        grouped.order_by(func.count().desc(), father_name_display.asc()).limit(limit)
    ).all()
    return [(row.father_name, row.patient_count) for row in rows], total
