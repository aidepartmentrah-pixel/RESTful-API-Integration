from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, LimitParam, OffsetParam
from app.core.security import require_api_key
from app.schemas.patient import Patient, PatientListResponse
from app.services import patient_service

router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
    dependencies=[Depends(require_api_key)],
)


@router.get("", response_model=PatientListResponse)
def search_patients(
    db: DbSession,
    patient_id: Annotated[str | None, Query()] = None,
    first_name: Annotated[str | None, Query(min_length=1)] = None,
    father_name: Annotated[str | None, Query(min_length=1)] = None,
    last_name: Annotated[str | None, Query(min_length=1)] = None,
    limit: LimitParam = 100,
    offset: OffsetParam = 0,
) -> PatientListResponse:
    items, total = patient_service.search_patients(
        db, patient_id, first_name, father_name, last_name, limit, offset
    )
    return PatientListResponse(
        items=[Patient.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{patient_id}", response_model=Patient)
def get_patient(db: DbSession, patient_id: str) -> Patient:
    patient = patient_service.get_patient(db, patient_id)
    return Patient.model_validate(patient)
