"""Merge the two 0008s: v1.2's HR tree (0008_hr, from main) and v1.3's BCI tables (0008)

Both revise 0007 and touch different tables, so this merge revision has no
schema changes of its own; it just joins the two heads into one.

Revision ID: 0009
Revises: 0008, 0008_hr
Create Date: 2026-11-18 00:00:01

"""
from typing import Sequence, Union

revision: str = "0009"
down_revision: Union[str, Sequence[str], None] = ("0008", "0008_hr")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
