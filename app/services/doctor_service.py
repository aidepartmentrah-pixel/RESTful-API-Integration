from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.doctor import Doctor
from app.repositories import doctor_repository


def search_doctors(
    db: Session, q: str | None, active_only: bool, limit: int, offset: int
) -> tuple[list[Doctor], int]:
    return doctor_repository.search_doctors(db, q, active_only, limit, offset)


def get_doctor(db: Session, doctor_id: str) -> Doctor:
    doctor = doctor_repository.get_doctor(db, doctor_id)
    if doctor is None:
        raise ApiError(
            status_code=404,
            error="DOCTOR_NOT_FOUND",
            message="The requested doctor was not found",
        )
    return doctor
