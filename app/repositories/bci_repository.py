from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.bci import BciPatient, BciVisit


def list_visits_with_patients(db: Session) -> list[tuple[BciVisit, BciPatient]]:
    # Deliberately no limit/offset -- requirement 1, section 5.
    stmt = (
        select(BciVisit, BciPatient)
        .join(BciPatient, BciPatient.mrn == BciVisit.mrn)
        .order_by(BciVisit.visit_clock.asc(), BciVisit.visit_id.asc())
    )
    return [(visit, patient) for visit, patient in db.execute(stmt).all()]


def get_patient_by_mrn(db: Session, mrn: str) -> BciPatient | None:
    return db.execute(select(BciPatient).where(BciPatient.mrn == mrn)).scalar_one_or_none()
