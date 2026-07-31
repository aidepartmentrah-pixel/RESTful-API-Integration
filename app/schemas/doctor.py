from pydantic import BaseModel, ConfigDict


class Doctor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doctor_id: str
    full_name: str
    specialty_id: str | None = None
    specialty_name: str | None = None
    department_id: str | None = None
    department_name: str | None = None
    is_active: bool


class DoctorListResponse(BaseModel):
    success: bool = True
    items: list[Doctor]
    total: int
    limit: int
    offset: int
