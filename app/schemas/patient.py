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
