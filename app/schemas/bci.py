from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class BciPersonNames(BaseModel):
    first_name_ar: str | None = None
    father_name_ar: str | None = None
    last_name_ar: str | None = None
    mother_name_ar: str | None = None
    first_name_en: str | None = None
    father_name_en: str | None = None
    last_name_en: str | None = None
    mother_name_en: str | None = None


class BciVisit(BciPersonNames):
    """PROPOSED v1.3 -- versions/v1.3/requirements/1-bci-radiology-visits-today/."""

    visit_id: str
    mrn: str
    birth_date: date | None = None
    sex: str | None = None
    visit_time: datetime
    visit_kind: str | None = None
    doctor_name: str | None = None
    status: str


class BciVisitListResponse(BaseModel):
    success: bool = True
    items: list[BciVisit]
    total: int


class BciPhone(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: str
    owner: str


class BciPatient(BciPersonNames):
    """PROPOSED v1.3 -- versions/v1.3/requirements/2-bci-radiology-patient/."""

    model_config = ConfigDict(from_attributes=True)

    mrn: str
    birth_date: date | None = None
    sex: str | None = None
    nationality: str | None = None
    id_number: str | None = None
    has_allergy: bool
    phones: list[BciPhone]
