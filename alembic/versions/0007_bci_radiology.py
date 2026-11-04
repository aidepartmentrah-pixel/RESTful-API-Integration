"""v1.3 proposed resources: bci_patients, bci_visits (/bci-radiology/*)

See versions/v1.3/requirements/. Own tables: the Directory's `patients`
table is not touched.

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-04 00:00:01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bci_patients",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("mrn", sa.String(length=64), nullable=False),
        sa.Column("first_name_ar", sa.String(length=128), nullable=True),
        sa.Column("father_name_ar", sa.String(length=128), nullable=True),
        sa.Column("last_name_ar", sa.String(length=128), nullable=True),
        sa.Column("mother_name_ar", sa.String(length=128), nullable=True),
        sa.Column("first_name_en", sa.String(length=128), nullable=True),
        sa.Column("father_name_en", sa.String(length=128), nullable=True),
        sa.Column("last_name_en", sa.String(length=128), nullable=True),
        sa.Column("mother_name_en", sa.String(length=128), nullable=True),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("sex", sa.String(length=32), nullable=True),
        sa.Column("nationality", sa.String(length=64), nullable=True),
        sa.Column("id_number", sa.String(length=64), nullable=True),
        sa.Column("has_allergy", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("phones", sa.JSON(), nullable=False),
    )
    op.create_index("ix_bci_patients_mrn", "bci_patients", ["mrn"], unique=True)

    op.create_table(
        "bci_visits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("visit_id", sa.String(length=64), nullable=False),
        sa.Column("mrn", sa.String(length=64), sa.ForeignKey("bci_patients.mrn"), nullable=False),
        sa.Column("visit_clock", sa.String(length=5), nullable=False),
        sa.Column("visit_kind", sa.String(length=16), nullable=True),
        sa.Column("doctor_name", sa.String(length=128), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
    )
    op.create_index("ix_bci_visits_visit_id", "bci_visits", ["visit_id"], unique=True)
    op.create_index("ix_bci_visits_mrn", "bci_visits", ["mrn"])


def downgrade() -> None:
    op.drop_index("ix_bci_visits_mrn", table_name="bci_visits")
    op.drop_index("ix_bci_visits_visit_id", table_name="bci_visits")
    op.drop_table("bci_visits")
    op.drop_index("ix_bci_patients_mrn", table_name="bci_patients")
    op.drop_table("bci_patients")
