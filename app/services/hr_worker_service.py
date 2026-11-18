"""GET /hr-workers - as 3iSoft delivered it ("HIS API - v1.2 Additions").

A worker's unit is the unit of their current basic job. Administration,
section and department are found by walking up the HR tree from that unit.

Filter rules (from 3iSoft's document):
  - filters take the unit NAME, not the id;
  - names are compared after trimming and unifying spelling:
    alef forms -> bare alef, ta marbuta -> ha, alef maqsura -> ya;
  - several filters are combined with AND;
  - a filter on a level returns that unit's workers and every unit below it
    (follows from comparing the walked-up names);
  - two units with the same name both match; inactive units still match;
  - an unknown name (or a name at the wrong level) gives an empty list;
  - an empty filter is ignored;
  - filtering happens before paging, so `total` counts matching workers.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.models.hr_unit import HrUnit
from app.models.worker import Worker

_SPELLING = str.maketrans({"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"})


def normalize_name(name: str | None) -> str:
    return (name or "").strip().translate(_SPELLING)


def _placement(units: dict[str, HrUnit], unit_id: str | None) -> dict[str, str | None]:
    found: dict[str, HrUnit] = {}
    seen: set[str] = set()
    while unit_id and unit_id in units and unit_id not in seen:
        seen.add(unit_id)
        unit = units[unit_id]
        found.setdefault(unit.level, unit)
        unit_id = unit.parent_unit_id
    out: dict[str, str | None] = {}
    for level in ("administration", "section", "department"):
        unit = found.get(level)
        out[f"{level}_id"] = unit.unit_id if unit else None
        out[f"{level}_name"] = unit.name if unit else None
    return out


def _to_hr_worker(worker: Worker, units: dict[str, HrUnit]) -> dict:
    return {
        "employee_id": worker.employee_id,
        "full_name": worker.full_name,
        "job_id": worker.job_id,
        "job_title": worker.job_title,
        **_placement(units, worker.hr_unit_id),
        "is_manager": worker.is_manager,
        "is_active": worker.is_active,
    }


def _units(db: Session) -> dict[str, HrUnit]:
    return {u.unit_id: u for u in db.execute(select(HrUnit)).scalars().all()}


def list_hr_workers(
    db: Session,
    administration: str | None,
    section: str | None,
    department: str | None,
    limit: int,
    offset: int,
) -> tuple[list[dict], int]:
    units = _units(db)
    workers = db.execute(select(Worker).order_by(Worker.full_name, Worker.employee_id)).scalars().all()
    rows = [_to_hr_worker(w, units) for w in workers]

    for level, value in (("administration", administration), ("section", section), ("department", department)):
        if value is None or not value.strip():
            continue  # an empty filter is ignored
        target = normalize_name(value)
        rows = [r for r in rows if r[f"{level}_name"] is not None and normalize_name(r[f"{level}_name"]) == target]

    return rows[offset:offset + limit], len(rows)


def get_hr_worker(db: Session, employee_id: str) -> dict:
    worker = db.execute(select(Worker).where(Worker.employee_id == employee_id)).scalars().first()
    if worker is None:
        raise ApiError(status_code=404, error="WORKER_NOT_FOUND", message="The requested worker was not found")
    return _to_hr_worker(worker, _units(db))
