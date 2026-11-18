from pydantic import BaseModel, ConfigDict


class Worker(BaseModel):
    """GET /workers - unchanged from v1.1 (3iSoft did not add unit names here)."""

    model_config = ConfigDict(from_attributes=True)

    employee_id: str
    full_name: str
    job_id: str | None = None
    job_title: str | None = None
    department_id: str | None = None
    department_name: str | None = None
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


class HrWorker(BaseModel):
    """GET /hr-workers - 3iSoft v1.2: the worker's place in the HR tree.

    Every field is always present (null when not known)."""

    employee_id: str
    full_name: str | None
    job_id: str | None
    job_title: str | None
    administration_id: str | None
    administration_name: str | None
    section_id: str | None
    section_name: str | None
    department_id: str | None
    department_name: str | None
    is_manager: bool | None
    is_active: bool


class HrWorkerListResponse(BaseModel):
    success: bool = True
    items: list[HrWorker]
    total: int
    limit: int
    offset: int
