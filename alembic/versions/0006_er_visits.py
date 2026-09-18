"""v1.2 proposed resource: er_visits (GET /er/current-visits)

See versions/v1.2/requirements/5-er-current-visits-hcopilot/requirement.md
for the rationale. No limit/offset by design -- see section 4 there.

Revision ID: 0006
Revises: 0005
Create Date: 2026-09-18 00:00:01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "er_visits",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("er_visit_id", sa.String(length=64), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("father_name", sa.String(length=128), nullable=False),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.Column("arrival_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("age", sa.Integer(), nullable=True),
        sa.Column("chief_complaint", sa.String(length=255), nullable=True),
    )
    op.create_index("ix_er_visits_er_visit_id", "er_visits", ["er_visit_id"], unique=True)
    op.create_index("ix_er_visits_arrival_time", "er_visits", ["arrival_time"])


def downgrade() -> None:
    op.drop_index("ix_er_visits_arrival_time", table_name="er_visits")
    op.drop_index("ix_er_visits_er_visit_id", table_name="er_visits")
    op.drop_table("er_visits")
