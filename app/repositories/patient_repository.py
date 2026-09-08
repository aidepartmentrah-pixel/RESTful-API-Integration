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
