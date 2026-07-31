"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-14 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "patient_visits",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column("visit_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("sex", sa.String(length=1), nullable=True),
        sa.Column("phone_number", sa.String(length=32), nullable=True),
        sa.Column("medical_file_number", sa.String(length=64), nullable=True),
        sa.Column("document_number", sa.String(length=64), nullable=True),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("departure_time", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("visit_id"),
    )
    op.create_index("ix_patient_visits_patient_id", "patient_visits", ["patient_id"])
    op.create_index("ix_patient_visits_visit_id", "patient_visits", ["visit_id"])
    op.create_index("ix_patient_visits_full_name", "patient_visits", ["full_name"])
    op.create_index("ix_patient_visits_phone_number", "patient_visits", ["phone_number"])
    op.create_index(
        "ix_patient_visits_medical_file_number", "patient_visits", ["medical_file_number"]
    )
    op.create_index("ix_patient_visits_document_number", "patient_visits", ["document_number"])

    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("doctor_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("specialty_id", sa.String(length=64), nullable=True),
        sa.Column("specialty_name", sa.String(length=128), nullable=True),
        sa.Column("department_id", sa.String(length=64), nullable=True),
        sa.Column("department_name", sa.String(length=128), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doctor_id"),
    )
    op.create_index("ix_doctors_doctor_id", "doctors", ["doctor_id"])
    op.create_index("ix_doctors_full_name", "doctors", ["full_name"])
    op.create_index("ix_doctors_specialty_name", "doctors", ["specialty_name"])
    op.create_index("ix_doctors_department_name", "doctors", ["department_name"])
    op.create_index("ix_doctors_is_active", "doctors", ["is_active"])

    op.create_table(
        "workers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("employee_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("job_id", sa.String(length=64), nullable=True),
        sa.Column("job_title", sa.String(length=128), nullable=True),
        sa.Column("department_id", sa.String(length=64), nullable=True),
        sa.Column("section_id", sa.String(length=64), nullable=True),
        sa.Column("administration_id", sa.String(length=64), nullable=True),
        sa.Column("is_manager", sa.Boolean(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id"),
    )
    op.create_index("ix_workers_employee_id", "workers", ["employee_id"])
    op.create_index("ix_workers_full_name", "workers", ["full_name"])
    op.create_index("ix_workers_job_title", "workers", ["job_title"])
    op.create_index("ix_workers_department_id", "workers", ["department_id"])
    op.create_index("ix_workers_section_id", "workers", ["section_id"])
    op.create_index("ix_workers_administration_id", "workers", ["administration_id"])
    op.create_index("ix_workers_is_active", "workers", ["is_active"])


def downgrade() -> None:
    op.drop_table("workers")
    op.drop_table("doctors")
    op.drop_table("patient_visits")
