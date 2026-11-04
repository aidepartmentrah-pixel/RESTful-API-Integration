from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.bci import BciPatient
from app.repositories import bci_repository
from app.schemas.bci import BciVisit

# The source system's local time (requirement 1, open item 4: to confirm).
BEIRUT = ZoneInfo("Asia/Beirut")


def beirut_today() -> date:
    """Today in Asia/Beirut. One definition; tests replace it to fix the day."""
    return datetime.now(BEIRUT).date()


def _source_down(exc: SQLAlchemyError) -> ApiError:
    # An unreadable source is an error, never an empty list (requirement 1, section 4).
    return ApiError(503, "SERVICE_UNAVAILABLE", "The source of visits is unavailable")


def list_visits_today(db: Session) -> list[BciVisit]:
    today = beirut_today()
    try:
        rows = bci_repository.list_visits_with_patients(db)
    except SQLAlchemyError as exc:
        raise _source_down(exc) from exc

    items = []
    for visit, patient in rows:
        hour, minute = (int(part) for part in visit.visit_clock.split(":"))
        items.append(
            BciVisit(
                visit_id=visit.visit_id,
                mrn=visit.mrn,
                first_name_ar=patient.first_name_ar,
                father_name_ar=patient.father_name_ar,
                last_name_ar=patient.last_name_ar,
                mother_name_ar=patient.mother_name_ar,
                first_name_en=patient.first_name_en,
                father_name_en=patient.father_name_en,
                last_name_en=patient.last_name_en,
                mother_name_en=patient.mother_name_en,
                birth_date=patient.birth_date,
                sex=patient.sex,
                # zoneinfo gives the offset valid on that day (+02:00 winter, +03:00 summer)
                visit_time=datetime.combine(today, time(hour, minute), tzinfo=BEIRUT),
                visit_kind=visit.visit_kind,
                doctor_name=visit.doctor_name,
                status=visit.status,
            )
        )
    return items


def get_patient(db: Session, mrn: str) -> BciPatient:
    try:
        patient = bci_repository.get_patient_by_mrn(db, mrn)
    except SQLAlchemyError as exc:
        raise _source_down(exc) from exc
    if patient is None:
        raise ApiError(404, "PATIENT_NOT_FOUND", "The requested patient was not found")
    return patient
