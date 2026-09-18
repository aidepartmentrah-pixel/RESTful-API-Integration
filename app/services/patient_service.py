from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.patient import Patient
from app.repositories import patient_repository

# OpenAPI v1.1: search must be patient_id, or all three of first_name/
# father_name/last_name together. Any other combination (a lone name field,
# or first+last without father) is rejected with this exact message.
_MISSING_CRITERIA_MESSAGE = (
    "Provide 'patient_id', or all three of 'first_name', 'father_name' and 'last_name'"
)


def search_patients(
    db: Session,
    patient_id: str | None,
    first_name: str | None,
    father_name: str | None,
    last_name: str | None,
    limit: int,
    offset: int,
) -> tuple[list[Patient], int]:
    has_full_name_trio = bool(first_name and father_name and last_name)

    if not patient_id and not has_full_name_trio:
        raise ApiError(
            status_code=422,
            error="VALIDATION_ERROR",
            message=_MISSING_CRITERIA_MESSAGE,
        )

    return patient_repository.search_patients(
        db, patient_id, first_name, father_name, last_name, limit, offset
    )


def get_patient(db: Session, patient_id: str) -> Patient:
    patient = patient_repository.get_patient(db, patient_id)
    if patient is None:
        raise ApiError(
            status_code=404,
            error="PATIENT_NOT_FOUND",
            message="The requested patient was not found",
        )
    return patient


def get_father_name_candidates(
    db: Session,
    first_name: str | None,
    last_name: str | None,
    limit: int,
) -> list[tuple[str, int]]:
    if not first_name or not last_name:
        raise ApiError(
            status_code=422,
            error="VALIDATION_ERROR",
            message="Both 'first_name' and 'last_name' are required",
        )
    return patient_repository.get_father_name_candidates(db, first_name, last_name, limit)


def get_first_name_candidates(
    db: Session,
    last_name: str | None,
    limit: int,
) -> list[tuple[str, int]]:
    if not last_name:
        raise ApiError(
            status_code=422,
            error="VALIDATION_ERROR",
            message="'last_name' is required",
        )
    return patient_repository.get_first_name_candidates(db, last_name, limit)
