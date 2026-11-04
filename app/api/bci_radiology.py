from fastapi import APIRouter, Depends

from app.api.deps import DbSession
from app.core.security import require_api_key
from app.schemas.bci import BciPatient, BciVisitListResponse
from app.services import bci_service

router = APIRouter(
    prefix="/bci-radiology",
    tags=["BCI Radiology"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/visits/today", response_model=BciVisitListResponse)
def list_visits_today(db: DbSession) -> BciVisitListResponse:
    items = bci_service.list_visits_today(db)
    return BciVisitListResponse(items=items, total=len(items))


@router.get("/patients/{mrn}", response_model=BciPatient)
def get_patient(db: DbSession, mrn: str) -> BciPatient:
    return BciPatient.model_validate(bci_service.get_patient(db, mrn))
