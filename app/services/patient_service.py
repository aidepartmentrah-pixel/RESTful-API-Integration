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
            status_code=400,
            error="MISSING_SEARCH_CRITERIA",
            message="At least one of q or patient_id is required",
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
