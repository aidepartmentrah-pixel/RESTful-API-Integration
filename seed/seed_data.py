"""Populates the mock database with fictional development data.

Run with: python -m seed.seed_data
"""
import random
from datetime import datetime, timedelta, timezone

from faker import Faker
from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import Doctor, ErVisit, HrUnit, Patient, Worker

SEED = 42
random.seed(SEED)

fake_en = Faker("en_US")
fake_ar = Faker("ar_SA")
Faker.seed(SEED)

TZ = timezone(timedelta(hours=3))

SPECIALTIES = [
    ("1", "Cardiology"),
    ("2", "Neurology"),
    ("3", "Orthopedics"),
    ("4", "Pediatrics"),
    ("5", "Dermatology"),
    ("6", "Oncology"),
    ("7", "Radiology"),
    ("8", "General Surgery"),
    ("9", "Internal Medicine"),
    ("10", "Emergency Medicine"),
]

DEPARTMENTS = [
    ("41", "Cardiac Care"),
    ("42", "Quality Assurance"),
    ("43", "Human Resources"),
    ("44", "Information Technology"),
    ("45", "Facilities"),
    ("46", "Finance"),
    ("47", "Nursing"),
    ("48", "Laboratory"),
]

SECTIONS = [
    ("1", "Inpatient Wards"),
    ("2", "Outpatient Clinics"),
    ("3", "Emergency Response"),
    ("4", "Surgical Services"),
    ("5", "Diagnostic Imaging"),
    ("6", "Pharmacy Operations"),
    ("7", "Records Management"),
    ("8", "Facilities Maintenance"),
    ("9", "Patient Transport"),
    ("10", "Central Supply"),
    ("11", "Billing"),
    ("12", "Volunteer Services"),
]

ADMINISTRATIONS = [
    ("1", "Medical Affairs"),
    ("2", "Nursing Affairs"),
    ("3", "Support Services"),
    ("4", "Finance & Administration"),
    ("5", "Quality & Patient Safety"),
]

CHIEF_COMPLAINTS = [
    "Chest pain",
    "Shortness of breath",
    "Abdominal pain",
    "Fever",
    "Laceration",
    "Fracture, suspected",
    "Headache, severe",
    "Allergic reaction",
]

JOB_TITLES = [
    "Nurse",
    "Receptionist",
    "Lab Technician",
    "Quality Assurance Specialist",
    "IT Support Engineer",
    "Pharmacist",
    "Administrator",
    "Security Officer",
    "Housekeeping Staff",
    "Accountant",
]


def random_person_names() -> dict[str, str | None]:
    """First/father/last name parts for one person.

    Arabic values are always populated (OpenAPI v1.1: full_name is built from
    the Arabic variants only). English values are populated for a random
    subset of fields, matching v1.1's "English name when stored, otherwise
    Arabic" fallback rule for first_name/last_name.
    """
    return {
        "first_name_ar": fake_ar.first_name(),
        "first_name_en": fake_en.first_name() if random.random() < 0.4 else None,
        "father_name_ar": fake_ar.first_name_male(),
        "father_name_en": fake_en.first_name_male() if random.random() < 0.4 else None,
        "last_name_ar": fake_ar.last_name(),
        "last_name_en": fake_en.last_name() if random.random() < 0.4 else None,
    }


def compute_age(birth_date) -> int:
    today = datetime.now(TZ).date()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def seed_patients(db) -> None:
    for patient_index in range(1, 101):
        patient_id = str(10000 + patient_index)
        names = random_person_names()

        has_birth_date = random.random() < 0.85
        birth_date = None
        age = None
        if has_birth_date:
            birth_date = fake_en.date_of_birth(minimum_age=1, maximum_age=95)
            age = compute_age(birth_date)
        elif random.random() < 0.5:
            age = random.randint(1, 95)

        # OpenAPI v1.1: sex is a display name resolved via a codes service,
        # not a fixed 1-char code.
        sex = random.choice(["Male", "Female"]) if random.random() < 0.95 else None

        db.add(
            Patient(
                patient_id=patient_id,
                birth_date=birth_date,
                age=age,
                sex=sex,
                **names,
            )
        )


def seed_doctors(db) -> None:
    for index in range(1, 51):
        doctor_id = str(1000 + index)
        names = random_person_names()
        full_name = f"Dr. {names['first_name_ar']} {names['father_name_ar']} {names['last_name_ar']}"
        specialty_id, specialty_name = random.choice(SPECIALTIES)
        is_active = random.random() < 0.85

        db.add(
            Doctor(
                doctor_id=doctor_id,
                full_name=full_name,
                first_name=names["first_name_ar"],
                father_name=names["father_name_ar"],
                last_name=names["last_name_ar"],
                assistant_number=f"A-{2000 + index}" if random.random() < 0.5 else None,
                specialty_id=specialty_id,
                specialty_name=specialty_name,
                # Always null today -- no department is modelled on Doctor
                # (OpenAPI v1.1).
                department_id=None,
                department_name=None,
                is_active=is_active,
            )
        )


def seed_workers(db) -> None:
    for index in range(1, 101):
        employee_id = str(5000 + index)
        names = random_person_names()
        full_name = f"{names['first_name_ar']} {names['father_name_ar']} {names['last_name_ar']}"
        job_title = random.choice(JOB_TITLES)
        department_id, department_name = random.choice(DEPARTMENTS)
        has_department = random.random() < 0.85
        section_id, _section_name = random.choice(SECTIONS)
        has_section = random.random() < 0.85
        administration_id, _administration_name = random.choice(ADMINISTRATIONS)
        has_administration = random.random() < 0.85
        is_active = random.random() < 0.85
        is_manager = random.choice([True, False]) if random.random() < 0.8 else None

        db.add(
            Worker(
                employee_id=employee_id,
                full_name=full_name,
                job_id=f"{200 + (index % 15)}" if random.random() < 0.8 else None,
                job_title=job_title,
                department_id=department_id if has_department else None,
                department_name=department_name if has_department else None,
                section_id=section_id if has_section else None,
                administration_id=administration_id if has_administration else None,
                is_manager=is_manager,
                is_active=is_active,
            )
        )


def seed_er_visits(db) -> None:
    """ER visits in the shape 3iSoft delivered (v1.2): Arabic names, gender
    as the Arabic word, age in whole years or null, free-text complaint."""
    now = datetime.now(TZ)
    for index in range(1, 19):
        er_visit_id = str(48200 + index)
        first_name = fake_ar.first_name()
        father_name = fake_ar.first_name_male()
        last_name = fake_ar.last_name()
        arrival_time = now - timedelta(minutes=random.randint(5, 480))
        gender = random.choice([GENDER_MALE_AR, GENDER_FEMALE_AR, None])
        age = random.randint(1, 95) if random.random() < 0.8 else None
        chief_complaint = random.choice(CHIEF_COMPLAINTS) if random.random() < 0.85 else None

        db.add(
            ErVisit(
                er_visit_id=er_visit_id,
                first_name=first_name,
                father_name=father_name,
                last_name=last_name,
                arrival_time=arrival_time,
                gender=gender,
                age=age,
                chief_complaint=chief_complaint,
            )
        )


# ---------------------------------------------------------------------------
# v1.2 as delivered by 3iSoft (18 Nov 2026). Idempotent: runs on fresh and on
# existing databases (the migrate step calls it every start).

GENDER_MALE_AR = "ذكر"
GENDER_FEMALE_AR = "انثى"

# (unit_id, name, level, parent_unit_id, is_active). Names deliberately include
# hamza/ta-marbuta spellings, one name used twice, and one inactive unit, so the
# /hr-workers filter rules have something to bite on.
HR_TREE = [
    ("6080.241", "الإدارة الطبية", "administration", None, True),
    ("6080.243", "دائرة التمريض", "section", "6080.241", True),
    ("6080.245", "قسم الطوارئ", "department", "6080.243", True),
    ("6080.246", "قسم العناية الفائقة", "department", "6080.243", True),
    ("6080.250", "دائرة الأطباء", "section", "6080.241", True),
    ("6080.251", "قسم الجراحة العامة", "department", "6080.250", True),
    ("6080.252", "قسم الأشعة", "department", "6080.250", True),
    ("6080.300", "الإدارة المالية", "administration", None, True),
    ("6080.301", "دائرة المحاسبة", "section", "6080.300", True),
    ("6080.302", "قسم الرواتب", "department", "6080.301", True),
    ("6080.303", "قسم الأرشيف", "department", "6080.301", True),
    ("6080.310", "دائرة المشتريات", "section", "6080.300", True),
    ("6080.400", "الإدارة العامة", "administration", None, True),
    ("6080.401", "دائرة الموارد البشرية", "section", "6080.400", True),
    ("6080.402", "قسم شؤون الموظفين", "department", "6080.401", True),
    ("6080.403", "قسم الأرشيف", "department", "6080.401", True),
    ("6080.404", "قسم التدريب القديم", "department", "6080.401", False),
]


def ensure_v1_2_delivered_data(db) -> None:
    changed = False
    if db.execute(select(HrUnit.id).limit(1)).first() is None:
        for unit_id, name, level, parent, active in HR_TREE:
            db.add(HrUnit(unit_id=unit_id, name=name, level=level, parent_unit_id=parent, is_active=active))
        changed = True

    workers = db.execute(select(Worker).order_by(Worker.employee_id)).scalars().all()
    if workers and all(w.hr_unit_id is None for w in workers):
        rng = random.Random(SEED)
        departments = [u for u in HR_TREE if u[2] == "department"]
        sections = [u for u in HR_TREE if u[2] == "section"]
        administrations = [u for u in HR_TREE if u[2] == "administration"]
        for worker in workers:
            roll = rng.random()
            if roll < 0.72:
                worker.hr_unit_id = rng.choice(departments)[0]      # usual case: in a department
            elif roll < 0.82:
                worker.hr_unit_id = rng.choice(sections)[0]         # placed directly in a section
            elif roll < 0.86:
                worker.hr_unit_id = rng.choice(administrations)[0]  # directly in an administration
            # else: no unit (the real server has workers without one too)
        changed = True

    for visit in db.execute(select(ErVisit).where(ErVisit.gender.in_(["Male", "Female"]))).scalars().all():
        visit.gender = GENDER_MALE_AR if visit.gender == "Male" else GENDER_FEMALE_AR
        changed = True

    if changed:
        db.commit()
        print("v1.2 delivered data ensured (HR tree, worker units, Arabic ER gender).")



def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.execute(select(Patient.id).limit(1)).first()
        if existing:
            print("Seed data already present. Skipping.")
            ensure_v1_2_delivered_data(db)
            return

        seed_patients(db)
        seed_doctors(db)
        seed_workers(db)
        seed_er_visits(db)
        db.commit()
        ensure_v1_2_delivered_data(db)
        print("Seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
