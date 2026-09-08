"""Populates the mock database with fictional development data.

Run with: python -m seed.seed_data
"""
import random
from datetime import datetime, timedelta, timezone

from faker import Faker
from sqlalchemy import select

from app.core.database import Base, SessionLocal, engine
from app.models import Doctor, Patient, Worker

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
                section_id=f"{random.randint(1, 12)}" if random.random() < 0.85 else None,
                administration_id=f"{random.randint(1, 5)}" if random.random() < 0.85 else None,
                is_manager=is_manager,
                is_active=is_active,
            )
        )


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        existing = db.execute(select(Patient.id).limit(1)).first()
        if existing:
            print("Seed data already present. Skipping.")
            return

        seed_patients(db)
        seed_doctors(db)
        seed_workers(db)
        db.commit()
        print("Seed data inserted successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
