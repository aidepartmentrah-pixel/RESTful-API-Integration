from pydantic import BaseModel, ConfigDict


class Worker(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    full_name: str
    job_id: str | None = None
    job_title: str | None = None
    department_id: str | None = None
    section_id: str | None = None
    administration_id: str | None = None
    is_manager: bool | None = None
    is_active: bool


class WorkerListResponse(BaseModel):
    success: bool = True
    items: list[Worker]
    total: int
    limit: int
    offset: int
