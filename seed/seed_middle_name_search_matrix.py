"""Seeds a deterministic search-matrix of patients for exercising the
middle-name-assist feature broadly: 5 base (first_name, last_name) pairs,
each combined with 20 of the 32 middle-name-assist candidate names, giving
100 real, individually-searchable patients with a genuine first/father/last
split.

Unlike seed_muslim_arabic_fixtures.py (a handful of hand-curated edge
cases, one row per specific matching quirk), this file exists to give a
HCAT tester VOLUME: many real chip-tap searches that actually return a
match, across several different first/last name pairs, so the
middle-name-assist UI can be exercised broadly rather than against a
single example. Every middle name used here is drawn from the same
32-name candidate list the real feature suggests as chips (see
name_sets/thirty_names.json in the "API Middle Name Coverage Test"
toolkit) -- unlike seed_muslim_arabic_fixtures.py's 90024, every record
here is deliberately a MATCH case; the "father name not in the list"
negative case is already covered there and isn't duplicated here.

Reserved ID range: 91001-91100 (100 patients), kept clear of both
seed_data.py's 10001+ range and seed_muslim_arabic_fixtures.py's
90001+ range.

Idempotent per-record, same pattern as seed_muslim_arabic_fixtures.py. Run
with:
    python -m seed.seed_middle_name_search_matrix
after seed_data.py (and, if wanted, seed_muslim_arabic_fixtures.py) have
already run.
"""
from datetime import date

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import Patient

# Base (first_name, last_name, sex) pairs. Deliberately distinct from every
# first/last name already used in seed_muslim_arabic_fixtures.py, so this
# file's records are easy to tell apart from the hand-curated edge cases.
BASE_NAME_PAIRS = [
    ("يوسف", "نعمة", "Male"),
    ("هدى", "دياب", "Female"),
    ("وليد", "بزي", "Male"),
    ("ليلى", "خشاب", "Female"),
    ("سامر", "طراد", "Male"),
]

# First 20 of the 32 middle-name-assist candidate names -- every record
# built from this list is therefore reachable by a real chip-tap query
# against father_name.
CANDIDATE_MIDDLE_NAMES = [
    "محمد", "علي", "حسين", "حسن", "عباس", "أحمد", "محمود", "مهدي",
    "مصطفى", "حيدر", "هادي", "رضا", "جعفر", "قاسم", "جواد", "مرتضى",
    "كاظم", "إبراهيم", "موسى", "إسماعيل",
]

PATIENT_ID_START = 91001


def _generate_patient_fixtures():
    """(patient_id, first_name_ar, father_name_ar, last_name_ar, birth_date,
    age, sex) for every (base pair) x (candidate middle name) combination --
    5 x 20 = 100 rows. birth_date is a deterministic, arbitrary spread
    across a plausible adult range, not meaningful data."""
    fixtures = []
    patient_id_num = PATIENT_ID_START
    for first_name, last_name, sex in BASE_NAME_PAIRS:
        for father_name in CANDIDATE_MIDDLE_NAMES:
            offset = patient_id_num - PATIENT_ID_START
            fixtures.append((
                str(patient_id_num),
                first_name,
                father_name,
                last_name,
                date(1965 + offset % 45, 1 + offset % 12, 1 + offset % 28),
                None,
                sex,
            ))
            patient_id_num += 1
    return fixtures


PATIENT_FIXTURES = _generate_patient_fixtures()


def seed_patients(db) -> int:
    """Inserts only the fixtures not already present. Returns the number of
    rows actually inserted."""
    existing_ids = {
        row[0] for row in db.execute(
            select(Patient.patient_id).where(
                Patient.patient_id.in_([f[0] for f in PATIENT_FIXTURES])
            )
        )
    }
    inserted = 0
    for patient_id, first_name_ar, father_name_ar, last_name_ar, birth_date, age, sex in PATIENT_FIXTURES:
        if patient_id in existing_ids:
            continue
        db.add(
            Patient(
                patient_id=patient_id,
                first_name_ar=first_name_ar,
                father_name_ar=father_name_ar,
                last_name_ar=last_name_ar,
                birth_date=birth_date,
                age=age,
                sex=sex,
            )
        )
        inserted += 1
    return inserted


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        inserted = seed_patients(db)
        db.commit()
        if not inserted:
            print("Middle-name search-matrix fixtures already present. Nothing to insert.")
            return
        print(f"Inserted {inserted} patients (middle-name search matrix) -- "
              f"{len(PATIENT_FIXTURES) - inserted} already present.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
