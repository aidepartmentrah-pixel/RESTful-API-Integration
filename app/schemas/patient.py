from datetime import date

from pydantic import BaseModel, ConfigDict


class Patient(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    full_name: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    age: int | None = None
    sex: str | None = None


class PatientListResponse(BaseModel):
    success: bool = True
    items: list[Patient]
    total: int
    limit: int
    offset: int


class FatherNameCandidate(BaseModel):
    father_name: str
    patient_count: int


class FatherNameCandidatesResponse(BaseModel):
    """See versions/v1.2/requirements/1-father-name-candidates/requirement.md
    for the rationale; implemented here so HCAT can develop against it while
    that ask is pending with the vendor."""

    success: bool = True
    first_name: str
    last_name: str
    candidates: list[FatherNameCandidate]
    # Distinct matches before `limit` is applied, so a caller can show
    # "showing 50 of 120".
    total_candidates: int

