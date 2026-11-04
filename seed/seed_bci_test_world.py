"""Seeds the BCI test world (v1.3): invented patients and today's visits.

Reads seed/bci_test_world.json, a copy of the BCI project's
testdata/patients.json (the BCI repo has a test that the two copies are
identical). Adds only patients whose MRN starts with "9999." and visits
whose id starts with "V9999-", one record at a time, only if missing:
safe to run on every start, never changes or deletes other rows.
The visit "time" is a clock time; the date is added when the API answers.

Run with: python -m seed.seed_bci_test_world
Remove with: python -m seed.seed_bci_test_world --remove
"""
import datetime
import json
import pathlib
import sys

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models import BciPatient, BciVisit

WORLD_FILE = pathlib.Path(__file__).parent / "bci_test_world.json"
MRN_PREFIX = "9999."
VISIT_PREFIX = "V9999-"


def patient_row(p: dict) -> BciPatient:
    ar, en = p["name_ar"], p["name_en"] or {}
    return BciPatient(
        mrn=p["mrn"],
        first_name_ar=ar["first"], father_name_ar=ar["father"],
        last_name_ar=ar["family"], mother_name_ar=ar["mother"],
        first_name_en=en.get("first"), father_name_en=en.get("father"),
        last_name_en=en.get("family"), mother_name_en=en.get("mother"),
        birth_date=datetime.date.fromisoformat(p["birth_date"]) if p["birth_date"] else None,
        sex=p["sex"],
        nationality=p["nationality"],
        id_number=p["id_number"],
        has_allergy=p["has_allergy"],
        phones=[{"number": ph["number"], "owner": ph["owner"]} for ph in p["phones"]],
    )


def load(db) -> tuple[int, int]:
    world = json.loads(WORLD_FILE.read_text(encoding="utf-8"))
    have_mrn = set(db.execute(select(BciPatient.mrn)).scalars())
    have_visit = set(db.execute(select(BciVisit.visit_id)).scalars())
    patients = visits = 0
    for p in world["patients"]:
        if not p["mrn"].startswith(MRN_PREFIX):
            continue
        if p["mrn"] not in have_mrn:
            db.add(patient_row(p))
            patients += 1
    db.flush()  # patients first: visits reference them
    for p in world["patients"]:
        for v in p["visits_today"]:
            if v["visit_id"].startswith(VISIT_PREFIX) and v["visit_id"] not in have_visit:
                db.add(BciVisit(
                    visit_id=v["visit_id"], mrn=p["mrn"], visit_clock=v["time"],
                    visit_kind=v["kind"], doctor_name=v["doctor"], status=v["status"],
                ))
                visits += 1
    db.commit()
    return patients, visits


def remove(db) -> tuple[int, int]:
    v = db.execute(delete(BciVisit).where(BciVisit.visit_id.like(VISIT_PREFIX + "%"))).rowcount
    p = db.execute(delete(BciPatient).where(BciPatient.mrn.like(MRN_PREFIX + "%"))).rowcount
    db.commit()
    return p, v


def main() -> None:
    db = SessionLocal()
    try:
        if sys.argv[1:] == ["--remove"]:
            print("removed patients=%d visits=%d" % remove(db))
        else:
            print("added patients=%d visits=%d" % load(db))
    finally:
        db.close()


if __name__ == "__main__":
    main()
