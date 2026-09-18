"""Seeds a curated, hand-authored set of Lebanese Muslim Arabic-name fixtures.

Unlike seed_data.py (random Faker output, not reproducible or independently
checkable against real people), every record here is a deliberately chosen
name + a deliberately engineered edge case, so a human can look at the
generated report and know exactly what was tested and why. Reserved ID
ranges (90001+, 9001+) keep these out of collision with the random seed.

Idempotent per-record: each fixture is only inserted if its ID isn't
already present, so rerunning after appending new fixtures to this file
still inserts the new ones instead of skipping everything because earlier
IDs already exist. Run with:
    python -m seed.seed_muslim_arabic_fixtures
after `docker compose up` (or any local run) has already run the normal
seed_data.py once.
"""
from datetime import date

from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import Doctor, Patient, Worker

# (patient_id, first_name_ar, father_name_ar, last_name_ar, birth_date, age,
# sex, note)
# `note` documents which specific search-matching edge case this row exists
# to probe -- kept out of the DB, used only by the toolkit's reference doc.
#
# OpenAPI v1.1 made patient search three separate structured fields
# (first_name/father_name/last_name), so these fixtures -- originally a
# single joined full_name string -- are now split into their real first/
# father/last parts. Two rows (90019, 90020) have no true father name in
# the source name at all (a compound given name forced into 3 words under
# the old single-string model); under the new model that's represented
# honestly as father_name_ar=None, which doubles as a realistic edge case:
# a real patient record with no father name on file is only findable by
# patient_id, never by the name-trio search.
PATIENT_FIXTURES = [
    ("90001", "علي", "محمد", "رحال", date(1988, 3, 14), None, "Male",
     "baseline 3-part Muslim name (first + father + last)"),
    ("90002", "محمد", "حسن", "الحاج", date(1975, 11, 2), None, "Male",
     "definite article (ال) inside last name"),
    ("90003", "حسن", "أحمد", "زعيتر", date(1990, 6, 21), None, "Male",
     "baseline 3-part Muslim name"),
    ("90004", "حسين", "علي", "خليل", date(1982, 1, 9), None, "Male",
     "baseline 3-part Muslim name"),
    ("90005", "أحمد", "خالد", "كرامي", date(1995, 9, 30), None, "Male",
     "baseline 3-part Muslim name, hamza in first name"),
    ("90006", "خالد", "حسين", "عيتاني", date(1970, 4, 17), None, "Male",
     "baseline 3-part Muslim name"),
    ("90007", "مصطفى", "محمد", "بيضون", date(2001, 12, 5), None, "Male",
     "alef maksura (ى) at end of first name"),
    ("90008", "بلال", "أحمد", "فقيه", date(1993, 7, 22), None, "Male",
     "baseline 3-part Muslim name"),
    ("90009", "فاطمة", "علي", "قاسم", date(1985, 2, 11), None, "Female",
     "teh marbuta (ة) in first name; father name is male even though patient is female"),
    ("90010", "زينب", "حسن", "حرب", date(1978, 8, 19), None, "Female",
     "baseline 3-part Muslim name, female patient"),
    ("90011", "رنا", "محمد", "حمادة", date(1999, 5, 3), None, "Female",
     "baseline 3-part Muslim name, female patient"),
    ("90012", "نور", "خالد", "جابر", date(1992, 10, 27), None, "Female",
     "baseline 3-part Muslim name, female patient"),
    ("90013", "عائشة", "حسين", "الموسوي", date(1980, 3, 8), None, "Female",
     "hamza-on-yeh (ئ) + definite article in last name"),
    ("90014", "سناء", "إبراهيم", "عسيران", date(1997, 1, 15), None, "Female",
     "terminal hamza (ء) in first name"),
    ("90015", "عليّ", "محمد", "رحال", date(1988, 3, 14), None, "Male",
     "shadda-diacritic variant of 90001's exact name -- tests whether "
     "search treats a diacritic mark as significant"),
    ("90016", "علي", "حسن", "حرب", date(1965, 6, 1), None, "Male",
     "duplicate pair A -- identical name to 90017, different person"),
    ("90017", "علي", "حسن", "حرب", date(2003, 9, 12), None, "Male",
     "duplicate pair B -- identical name to 90016, different person "
     "(contract requires both returned, never deduped/merged)"),
    ("90018", "محمد", "حسن", "رحال", date(1991, 4, 4), None, "Male",
     "the exact 3-word first+father+last query real-evidence used against "
     "the real server (10 real matches there) -- kept identical here"),
    ("90019", "أبو بكر", None, "خليل", date(1969, 11, 30), None, "Male",
     "compound kunya-style given name with no distinct father name on "
     "file -- only findable by patient_id, never by the name-trio search "
     "(father_name is required and this record has none)"),
    ("90020", "عبد الرحمن", None, "الفقيه", date(1987, 7, 7), None, "Male",
     "theophoric compound given name with no distinct father name on file "
     "-- same 'patient_id-only' edge case as 90019"),
    ("90021", "زينب", "محمد", "نصار", date(1994, 5, 12), None, "Female",
     "middle-name-assist test: father name محمد IS in the 32-name candidate "
     "list -- a chip-tap query (زينب + محمد chip + نصار) should match"),
    ("90022", "علي", "حسين", "زهر الدين", date(1983, 9, 2), None, "Male",
     "middle-name-assist test: father name حسين IS in the 32-name candidate "
     "list; two-word last name (زهر الدين) -- chip-tap query should still "
     "match via substring on the last_name field"),
    ("90023", "كريم", "عباس", "شمس الدين", date(1990, 12, 20), None, "Male",
     "middle-name-assist test: father name عباس IS in the 32-name candidate "
     "list; two-word last name (شمس الدين) -- chip-tap query should still "
     "match via substring on the last_name field"),
    ("90024", "مريم", "توفيق", "عيتاني", date(1996, 2, 18), None, "Female",
     "middle-name-assist test: father name توفيق is NOT in the 32-name "
     "candidate list -- every candidate-chip query against this patient "
     "should honestly return zero results (tests the add-as-new path)"),
]

# Two duplicate-name GROUPS (20 + 20 = 40 patients, ids 90025-90064): same
# first_name_ar + last_name_ar in both groups, but a different father_name_ar
# per group -- i.e. two genuinely different real people/families who share a
# first+last name, each with a large number of duplicate-looking rows of
# their own. Added to reproduce a suspected production bug: when a search
# for one father-name group returns a big pile of duplicates, does the
# *other*, differently-fathered group still surface its own full result set,
# or does the first group somehow prevent the second from ever appearing?
# The three-field search is supposed to AND first_name/father_name/last_name
# independently per column, so these two groups should never interact --
# this fixture set exists to prove that empirically against a running
# server, not just by reading the repository code.
_DUPLICATE_GROUP_FIRST_NAME_AR = "عباس"
_DUPLICATE_GROUP_LAST_NAME_AR = "زهرالدين"
_DUPLICATE_GROUP_FATHER_NAMES = [("A", "محمد"), ("B", "حسن")]


def _duplicate_group_fixtures():
    fixtures = []
    patient_id_num = 90025
    for group_label, father_name_ar in _DUPLICATE_GROUP_FATHER_NAMES:
        other_label = "B" if group_label == "A" else "A"
        for i in range(20):
            birth_date = date(1965 + i, 1 + (i * 7) % 12, 1 + (i * 3) % 28)
            fixtures.append((
                str(patient_id_num),
                _DUPLICATE_GROUP_FIRST_NAME_AR,
                father_name_ar,
                _DUPLICATE_GROUP_LAST_NAME_AR,
                birth_date,
                None,
                "Male",
                f"duplicate-name-group {group_label}, record {i + 1}/20: same "
                f"first+last name as group {other_label}, different father name "
                f"({father_name_ar}) -- a genuinely different real person/group. "
                f"Searching father_name='{father_name_ar}' must return exactly this "
                f"group's 20 rows, independent of group {other_label}'s 20 rows.",
            ))
            patient_id_num += 1
    return fixtures


PATIENT_FIXTURES = PATIENT_FIXTURES + _duplicate_group_fixtures()

# Two more duplicate-name GROUPS (20 + 20 = 40 patients, ids 90065-90104).
# Same first_name_ar/last_name_ar as the 90025-90064 groups above, but
# DIFFERENT father names (خالد/أحمد, not محمد/حسن) -- deliberately, so a
# father_name search can't accidentally merge this set with the
# 90025-90064 one (an earlier version of this fixture reused محمد/حسن here
# and every search returned 40 merged rows instead of a clean 20, which
# defeated both tests). Data shape: every record WITHIN a group shares the
# SAME birth_date (representing one real person recorded many times --
# e.g. one row per hospital admission, since the vendor's real data is
# admission-centric, not person-centric), while the two groups' birth
# dates differ from each other (distinguishable as two different real
# people who happen to share a name, same convention as 90016/90017).
# Requested by the HCAT team to test their own dedup logic end-to-end
# against this mock ("same name + same birth_date = one real person
# re-entered; same name + different birth_date = two real people") -- a
# different question from the 90025-90064 groups above, which test
# whether one group's search can block another's. This mock returns all
# 40 raw rows unmodified; the dedup itself is HCAT's concern on receipt,
# not this API's.
_DUPLICATE_GROUP_SAME_BIRTH_DATE_GROUPS = [
    ("A2", "خالد", date(1980, 5, 10)),
    ("B2", "أحمد", date(1975, 3, 22)),
]


def _duplicate_group_same_birth_date_fixtures():
    fixtures = []
    patient_id_num = 90065
    for group_label, father_name_ar, birth_date in _DUPLICATE_GROUP_SAME_BIRTH_DATE_GROUPS:
        other_label = "B2" if group_label == "A2" else "A2"
        for i in range(20):
            fixtures.append((
                str(patient_id_num),
                _DUPLICATE_GROUP_FIRST_NAME_AR,
                father_name_ar,
                _DUPLICATE_GROUP_LAST_NAME_AR,
                birth_date,
                None,
                "Male",
                f"duplicate-name-group {group_label}, record {i + 1}/20: same "
                f"first+last name as group {other_label}, different father name "
                f"({father_name_ar}), and ALL 20 rows in this group share the same "
                f"birth_date ({birth_date}) -- one real person recorded 20 times "
                f"(one row per admission). Group {other_label} shares this group's "
                f"first+last name but has its own distinct shared birth_date, so "
                f"the two groups are a different real person each. Tests HCAT's "
                f"dedup logic: same name+birth_date collapses to one person, "
                f"different birth_date stays two.",
            ))
            patient_id_num += 1
    return fixtures


PATIENT_FIXTURES = PATIENT_FIXTURES + _duplicate_group_same_birth_date_fixtures()

DOCTOR_FIXTURES = [
    ("9001", "حيدر", "علي", "رحال", "1", "Cardiology"),
    ("9002", "جعفر", "حسن", "زعيتر", "9", "Internal Medicine"),
    ("9003", "هبة", "علي", "قاسم", "4", "Pediatrics"),
    ("9004", "خالد", "حسين", "عيتاني", "8", "General Surgery"),
    ("9005", "عائشة", "محمد", "الموسوي", "7", "Radiology"),
]

WORKER_FIXTURES = [
    ("9001", "وائل حسن فقيه", "Security Officer"),
    ("9002", "رنا علي حمادة", "Nurse"),
    ("9003", "مصطفى خالد بيضون", "Lab Technician"),
    ("9004", "سناء محمد عسيران", "Receptionist"),
    ("9005", "نور حسين جابر", "Pharmacist"),
]


def seed_patients(db) -> int:
    """Inserts only the fixtures not already present, so appending new rows
    to PATIENT_FIXTURES later still gets them inserted into a database that
    already has an earlier subset -- not silently skipped. Returns the
    number of rows actually inserted."""
    existing_ids = {
        row[0] for row in db.execute(
            select(Patient.patient_id).where(
                Patient.patient_id.in_([f[0] for f in PATIENT_FIXTURES])
            )
        )
    }
    inserted = 0
    for patient_id, first_name_ar, father_name_ar, last_name_ar, birth_date, age, sex, _note in PATIENT_FIXTURES:
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


def seed_doctors(db) -> int:
    existing_ids = {
        row[0] for row in db.execute(
            select(Doctor.doctor_id).where(
                Doctor.doctor_id.in_([f[0] for f in DOCTOR_FIXTURES])
            )
        )
    }
    inserted = 0
    for doctor_id, first_name, father_name, last_name, specialty_id, specialty_name in DOCTOR_FIXTURES:
        if doctor_id in existing_ids:
            continue
        db.add(
            Doctor(
                doctor_id=doctor_id,
                full_name=f"Dr. {first_name} {father_name} {last_name}",
                first_name=first_name,
                father_name=father_name,
                last_name=last_name,
                specialty_id=specialty_id,
                specialty_name=specialty_name,
                department_id=None,
                department_name=None,
                is_active=True,
            )
        )
        inserted += 1
    return inserted


def seed_workers(db) -> int:
    existing_ids = {
        row[0] for row in db.execute(
            select(Worker.employee_id).where(
                Worker.employee_id.in_([f[0] for f in WORKER_FIXTURES])
            )
        )
    }
    inserted = 0
    for employee_id, full_name, job_title in WORKER_FIXTURES:
        if employee_id in existing_ids:
            continue
        db.add(
            Worker(
                employee_id=employee_id,
                full_name=full_name,
                job_id=None,
                job_title=job_title,
                department_id=None,
                department_name=None,
                section_id=None,
                administration_id=None,
                is_manager=None,
                is_active=True,
            )
        )
        inserted += 1
    return inserted


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        patients_inserted = seed_patients(db)
        doctors_inserted = seed_doctors(db)
        workers_inserted = seed_workers(db)
        db.commit()
        if not (patients_inserted or doctors_inserted or workers_inserted):
            print("Muslim Arabic fixtures already present. Nothing to insert.")
            return
        print(f"Inserted {patients_inserted} patients, {doctors_inserted} "
              f"doctors, {workers_inserted} workers (Muslim Arabic fixtures) "
              f"-- {len(PATIENT_FIXTURES) - patients_inserted} patients, "
              f"{len(DOCTOR_FIXTURES) - doctors_inserted} doctors, "
              f"{len(WORKER_FIXTURES) - workers_inserted} workers already present.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
