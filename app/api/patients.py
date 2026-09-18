from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import DbSession, LimitParam, OffsetParam
from app.core.security import require_api_key
from app.schemas.patient import (
    FatherNameCandidate,
    FatherNameCandidatesResponse,
    FirstNameCandidate,
    FirstNameCandidatesResponse,
    Patient,
    PatientListResponse,
)
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


# Registered before /{patient_id} -- a literal sub-path must win over the
# dynamic path parameter, or "father-names" would be swallowed as a
# patient_id value instead of matching this route.
@router.get("/father-names", response_model=FatherNameCandidatesResponse)
def get_father_name_candidates(
    db: DbSession,
    first_name: Annotated[str | None, Query(min_length=1)] = None,
    last_name: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> FatherNameCandidatesResponse:
    candidates = patient_service.get_father_name_candidates(db, first_name, last_name, limit)
    return FatherNameCandidatesResponse(
        first_name=first_name or "",
        last_name=last_name or "",
        candidates=[
            FatherNameCandidate(father_name=father_name, patient_count=count)
            for father_name, count in candidates
        ],
        total_candidates=len(candidates),
    )


# Registered before /{patient_id} for the same reason as /father-names above.
@router.get("/first-names", response_model=FirstNameCandidatesResponse)
def get_first_name_candidates(
    db: DbSession,
    last_name: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> FirstNameCandidatesResponse:
    candidates = patient_service.get_first_name_candidates(db, last_name, limit)
    return FirstNameCandidatesResponse(
        last_name=last_name or "",
        candidates=[
            FirstNameCandidate(first_name=first_name, patient_count=count)
            for first_name, count in candidates
        ],
        total_candidates=len(candidates),
    )


@router.get("/{patient_id}", response_model=Patient)
def get_patient(db: DbSession, patient_id: str) -> Patient:
    patient = patient_service.get_patient(db, patient_id)
    return Patient.model_validate(patient)
