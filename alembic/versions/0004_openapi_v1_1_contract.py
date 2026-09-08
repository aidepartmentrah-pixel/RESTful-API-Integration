"""OpenAPI v1.1: structured patient name search + doctor search fields

Patients move from a single (full_name, first_name, last_name) blob to six
Arabic/English name-part columns (first/father/last x ar/en), matching the
v1.1 contract's per-column first_name/father_name/last_name search with
Arabic-or-English matching. full_name/first_name/last_name are now derived
in Python from these columns rather than stored directly. `sex` widens from
a 1-char code to a resolved display string.

Doctors gain first_name/father_name/last_name/assistant_number columns --
not exposed in the Doctor response, but needed so `q` can OR-match against
them per v1.1.

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-08 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_patients_full_name", table_name="patients")
    op.drop_column("patients", "full_name")
    op.drop_column("patients", "first_name")
    op.drop_column("patients", "last_name")

    op.add_column("patients", sa.Column("first_name_ar", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("first_name_en", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("father_name_ar", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("father_name_en", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("last_name_ar", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("last_name_en", sa.String(length=128), nullable=True))
    op.create_index("ix_patients_first_name_ar", "patients", ["first_name_ar"])
    op.create_index("ix_patients_first_name_en", "patients", ["first_name_en"])
    op.create_index("ix_patients_father_name_ar", "patients", ["father_name_ar"])
    op.create_index("ix_patients_father_name_en", "patients", ["father_name_en"])
    op.create_index("ix_patients_last_name_ar", "patients", ["last_name_ar"])
    op.create_index("ix_patients_last_name_en", "patients", ["last_name_en"])

    op.alter_column("patients", "sex", type_=sa.String(length=32))

    op.add_column("doctors", sa.Column("first_name", sa.String(length=128), nullable=True))
    op.add_column("doctors", sa.Column("father_name", sa.String(length=128), nullable=True))
    op.add_column("doctors", sa.Column("last_name", sa.String(length=128), nullable=True))
    op.add_column("doctors", sa.Column("assistant_number", sa.String(length=64), nullable=True))
    op.create_index("ix_doctors_first_name", "doctors", ["first_name"])
    op.create_index("ix_doctors_father_name", "doctors", ["father_name"])
    op.create_index("ix_doctors_last_name", "doctors", ["last_name"])
    op.create_index("ix_doctors_assistant_number", "doctors", ["assistant_number"])


def downgrade() -> None:
    op.drop_index("ix_doctors_assistant_number", table_name="doctors")
    op.drop_index("ix_doctors_last_name", table_name="doctors")
    op.drop_index("ix_doctors_father_name", table_name="doctors")
    op.drop_index("ix_doctors_first_name", table_name="doctors")
    op.drop_column("doctors", "assistant_number")
    op.drop_column("doctors", "last_name")
    op.drop_column("doctors", "father_name")
    op.drop_column("doctors", "first_name")

    op.alter_column("patients", "sex", type_=sa.String(length=1))

    op.drop_index("ix_patients_last_name_en", table_name="patients")
    op.drop_index("ix_patients_last_name_ar", table_name="patients")
    op.drop_index("ix_patients_father_name_en", table_name="patients")
    op.drop_index("ix_patients_father_name_ar", table_name="patients")
    op.drop_index("ix_patients_first_name_en", table_name="patients")
    op.drop_index("ix_patients_first_name_ar", table_name="patients")
    op.drop_column("patients", "last_name_en")
    op.drop_column("patients", "last_name_ar")
    op.drop_column("patients", "father_name_en")
    op.drop_column("patients", "father_name_ar")
    op.drop_column("patients", "first_name_en")
    op.drop_column("patients", "first_name_ar")

    op.add_column("patients", sa.Column("last_name", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("first_name", sa.String(length=128), nullable=True))
    op.add_column("patients", sa.Column("full_name", sa.String(length=255), nullable=False, server_default=""))
    op.create_index("ix_patients_full_name", "patients", ["full_name"])
