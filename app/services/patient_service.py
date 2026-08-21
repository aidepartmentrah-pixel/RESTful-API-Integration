from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.patient import Patient
from app.repositories import patient_repository


def search_patients(
    db: Session,
    q: str | None,
    patient_id: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Patient], int]:
    if not any([q, patient_id]):
        raise ApiError(
            status_code=422,
            error="VALIDATION_ERROR",
            message="At least one of 'q' or 'patient_id' is required",
        )

    # The real vendor API rejects a name search that isn't a complete name
    # (confirmed: a single word gets a 422). Our Patient model only stores
    # first+last (no father/middle name), so we can't reproduce the vendor's
    # exact 3-word rule -- this enforces the same class of validation (a
    # bare word isn't a name search) using the 2-word minimum our own data
    # actually supports.
    if q and len(q.split()) < 2:
        raise ApiError(
            status_code=422,
            error="VALIDATION_ERROR",
            message="Please enter the patient's full name, not just part of the name",
        )

    return patient_repository.search_patients(db, q, patient_id, limit, offset)


def get_patient(db: Session, patient_id: str) -> Patient:
    patient = patient_repository.get_patient(db, patient_id)
    if patient is None:
        raise ApiError(
            status_code=404,
            error="PATIENT_NOT_FOUND",
            message="The requested patient was not found",
        )
    return patient
