from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.patient import Patient


def search_patients(
    db: Session,
    q: str | None,
    patient_id: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Patient], int]:
    stmt = select(Patient)

    if patient_id:
        stmt = stmt.where(Patient.patient_id == patient_id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(
            or_(
                Patient.patient_id.ilike(like),
                Patient.full_name.ilike(like),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    stmt = stmt.order_by(Patient.patient_id).limit(limit).offset(offset)
    items = list(db.execute(stmt).scalars().all())

    return items, total


def get_patient(db: Session, patient_id: str) -> Patient | None:
    stmt = select(Patient).where(Patient.patient_id == patient_id)
    return db.execute(stmt).scalars().first()
