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


def random_name() -> tuple[str, str, str]:
    """Returns (full_name, first_name, last_name) in Arabic or English."""
    if random.random() < 0.5:
        first = fake_ar.first_name()
        last = fake_ar.last_name()
    else:
        first = fake_en.first_name()
        last = fake_en.last_name()
    return f"{first} {last}", first, last


def compute_age(birth_date) -> int:
    today = datetime.now(TZ).date()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def seed_patients(db) -> None:
    for patient_index in range(1, 101):
        patient_id = f"P-{10000 + patient_index}"
        full_name, first_name, last_name = random_name()

        has_birth_date = random.random() < 0.85
        birth_date = None
        age = None
        if has_birth_date:
            birth_date = fake_en.date_of_birth(minimum_age=1, maximum_age=95)
            age = compute_age(birth_date)
        elif random.random() < 0.5:
            age = random.randint(1, 95)

        sex = random.choice(["M", "F"]) if random.random() < 0.95 else None

        db.add(
            Patient(
                patient_id=patient_id,
                full_name=full_name,
                first_name=first_name,
                last_name=last_name,
                birth_date=birth_date,
                age=age,
                sex=sex,
            )
        )


def seed_doctors(db) -> None:
    for index in range(1, 51):
        doctor_id = f"D-{1000 + index}"
        full_name, _, _ = random_name()
        specialty_id, specialty_name = random.choice(SPECIALTIES)
        department_id, department_name = random.choice(DEPARTMENTS)
        is_active = random.random() < 0.85

        db.add(
            Doctor(
                doctor_id=doctor_id,
                full_name=f"Dr. {full_name}",
                specialty_id=specialty_id,
                specialty_name=specialty_name,
                department_id=department_id if random.random() < 0.9 else None,
                department_name=department_name if random.random() < 0.9 else None,
                is_active=is_active,
            )
        )


def seed_workers(db) -> None:
    for index in range(1, 101):
        employee_id = f"E-{5000 + index}"
        full_name, _, _ = random_name()
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
