"""v1.2 proposed additions: Patient.encounter_type, Worker.section_name/administration_name

See versions/v1.2/requirements/3-worker-section-administration-names/ and
versions/v1.2/requirements/4-patient-encounter-type/ for the rationale.
Both are nullable display-name/status fields, same convention already
used for Worker.department_name (0003).

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-18 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("encounter_type", sa.String(length=32), nullable=True))

    op.add_column("workers", sa.Column("section_name", sa.String(length=128), nullable=True))
    op.create_index("ix_workers_section_name", "workers", ["section_name"])
    op.add_column("workers", sa.Column("administration_name", sa.String(length=128), nullable=True))
    op.create_index("ix_workers_administration_name", "workers", ["administration_name"])


def downgrade() -> None:
    op.drop_index("ix_workers_administration_name", table_name="workers")
    op.drop_column("workers", "administration_name")
    op.drop_index("ix_workers_section_name", table_name="workers")
    op.drop_column("workers", "section_name")

    op.drop_column("patients", "encounter_type")
