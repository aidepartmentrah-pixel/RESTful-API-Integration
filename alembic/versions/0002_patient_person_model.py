"""patient_visits -> patients (person-level model, drops visit fields)

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-20 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("patient_visits")

    op.create_table(
        "patients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("patient_id", sa.String(length=64), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=True),
        sa.Column("last_name", sa.String(length=128), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("sex", sa.String(length=1), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("patient_id"),
    )
    op.create_index("ix_patients_patient_id", "patients", ["patient_id"])
    op.create_index("ix_patients_full_name", "patients", ["full_name"])


def downgrade() -> None:
    op.drop_table("patients")

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
