"""v1.2 as delivered by 3iSoft: HR tree for /hr-workers; ER names nullable

3iSoft's "HIS API - v1.2 Additions" (18 Nov 2026) delivered worker units as a
new GET /hr-workers (administration > section > department, walked up from
the worker's basic-job unit) instead of section_name/administration_name on
/workers. So:
  - hr_units: the HR organisational tree.
  - workers.hr_unit_id: the unit of the worker's current basic job.
  - workers.section_name / administration_name (our 0005 proposal) dropped:
    the real /workers did not change.
  - er_visits names nullable: 3iSoft returns null for any missing value.

Revision id is "0008_hr" (not "0008") so it does not collide with the v1.3
branch's own 0008 (BCI radiology); v1.3 joins the two with a merge revision.

Revision ID: 0008_hr
Revises: 0007
Create Date: 2026-11-18 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0008_hr"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "hr_units",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("unit_id", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("level", sa.String(length=32), nullable=False),
        sa.Column("parent_unit_id", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_hr_units_unit_id", "hr_units", ["unit_id"], unique=True)

    op.add_column("workers", sa.Column("hr_unit_id", sa.String(length=64), nullable=True))
    op.create_index("ix_workers_hr_unit_id", "workers", ["hr_unit_id"])
    op.drop_column("workers", "section_name")
    op.drop_column("workers", "administration_name")

    for column in ("first_name", "father_name", "last_name"):
        op.alter_column("er_visits", column, existing_type=sa.String(length=128), nullable=True)


def downgrade() -> None:
    for column in ("first_name", "father_name", "last_name"):
        op.execute(f"UPDATE er_visits SET {column} = '' WHERE {column} IS NULL")
        op.alter_column("er_visits", column, existing_type=sa.String(length=128), nullable=False)

    op.add_column("workers", sa.Column("administration_name", sa.String(length=128), nullable=True))
    op.add_column("workers", sa.Column("section_name", sa.String(length=128), nullable=True))
    op.drop_index("ix_workers_hr_unit_id", table_name="workers")
    op.drop_column("workers", "hr_unit_id")
    op.drop_index("ix_hr_units_unit_id", table_name="hr_units")
    op.drop_table("hr_units")
