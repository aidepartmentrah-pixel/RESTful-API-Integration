"""v1.2 scope cut: drop Patient.encounter_type

Decided in the 4 Nov 2026 meeting: the source system does not record
inpatient/outpatient, so the field cannot be supplied by the vendor.
0005 is left as-is (already applied on dev databases, and it also adds the
Worker section/administration name columns that stay in v1.2).

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-04 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("patients", "encounter_type")


def downgrade() -> None:
    op.add_column("patients", sa.Column("encounter_type", sa.String(length=32), nullable=True))
