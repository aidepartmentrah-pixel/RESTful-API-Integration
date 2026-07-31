from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, LimitParam, OffsetParam
from app.core.security import require_api_key
from app.schemas.doctor import Doctor, DoctorListResponse
from app.services import doctor_service

router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=DoctorListResponse)
def search_doctors(
    db: DbSession,
    q: Annotated[str | None, Query(min_length=1)] = None,
    active_only: Annotated[bool, Query()] = True,
    limit: LimitParam = 100,
    offset: OffsetParam = 0,
) -> DoctorListResponse:
    items, total = doctor_service.search_doctors(db, q, active_only, limit, offset)
    return DoctorListResponse(
        items=[Doctor.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{doctor_id}", response_model=Doctor)
def get_doctor(db: DbSession, doctor_id: str) -> Doctor:
    doctor = doctor_service.get_doctor(db, doctor_id)
    return Doctor.model_validate(doctor)
