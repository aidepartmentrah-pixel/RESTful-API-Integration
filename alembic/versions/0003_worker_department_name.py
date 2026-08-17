"""workers: add department_name (confirmed against the real API - see vendor-deliverable/API_Implementation_Requirements.md)

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-24 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("workers", sa.Column("department_name", sa.String(length=128), nullable=True))
    op.create_index("ix_workers_department_name", "workers", ["department_name"])


def downgrade() -> None:
    op.drop_index("ix_workers_department_name", table_name="workers")
    op.drop_column("workers", "department_name")
